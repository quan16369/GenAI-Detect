from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

from ..arc_public_envs import find_public_knowledge
from ..client import AcontextClient
from ..models import Skill


DistillFn = Callable[[list[dict[str, str]]], str]


@dataclass(slots=True)
class _SkillRefs:
    shared: Skill
    game: Skill
    verified: Skill | None = None


class ArcSkillMemory:
    """Kaggle-friendly ARC-AGI-3 memory built on top of the local Acontext client."""

    MECHANIC_TEMPLATE = """# Game Mechanic: {game_id}

## Action Effects
- ACTION1: unknown
- ACTION2: unknown
- ACTION3: unknown
- ACTION4: unknown
- ACTION5: unknown
- ACTION6 (x,y): unknown

## Win Condition
unknown

## Discovered Patterns
none yet
"""

    FAILURE_TEMPLATE = """# Failure Log: {game_id}

## Failed Sequences
none yet

## Dead-End States
none yet

## Actions With No Effect
none yet
"""

    STRATEGY_TEMPLATE = """# Strategy: {game_id} - Level {level}

## Current Hypothesis
unknown - explore first

## Next Actions To Try
1. Explore ACTION1-ACTION5 to observe effects
2. Try ACTION6 on colored or distinct cells
3. Avoid repeating actions with no effect

## Progress
Level {level} - {actions} actions taken
"""

    SHARED_TEMPLATE = """# Cross-Game Pattern Library

## Recurring Mechanics
none yet

## Reliable Exploration Strategies
- Always try ACTION1-ACTION5 first on a new level to observe effects
- ACTION6 on standout cells often reveals hidden interactions
- If stuck for several actions, invert the last pattern you trusted

## Anti-Patterns
- Repeating the same action three times with no frame change
"""

    def __init__(
        self,
        game_id: str,
        *,
        client: AcontextClient | None = None,
        storage_dir: str | None = None,
        learning_space_name: str = "arc-agi-3",
        distill_fn: DistillFn | None = None,
        public_summary_path: str | None = None,
        public_environment_root: str | None = None,
        include_verified_public: bool = True,
    ) -> None:
        self.game_id = game_id
        self.client = client or AcontextClient(storage_dir=storage_dir)
        self.learning_space_name = learning_space_name
        self.distill_fn = distill_fn
        self.include_verified_public = include_verified_public
        self.public_knowledge = (
            find_public_knowledge(
                report_path=public_summary_path,
                environment_root=public_environment_root,
            )
            if include_verified_public
            else None
        )
        self.space = self._ensure_space()
        self.refs = self._ensure_skill_set()

    def _ensure_space(self):
        for space in self.client.learning_spaces.list().items:
            if space.meta.get("name") == self.learning_space_name:
                return space
        return self.client.learning_spaces.create(meta={"name": self.learning_space_name, "kind": "arc_agi3"})

    def _find_space_skill(self, name: str) -> Skill | None:
        for skill in self.client.learning_spaces.list_skills(self.space.id):
            if skill.name == name:
                return skill
        return None

    def _ensure_skill(self, name: str, description: str, files: dict[str, str]) -> Skill:
        existing = self._find_space_skill(name)
        target_id = existing.id if existing else None
        skill = self.client.skills.upsert_files(
            name=name,
            description=description,
            files=files,
            skill_id=target_id,
            meta={"kind": "arc_agi3"},
        )
        self.client.learning_spaces.include_skill(self.space.id, skill_id=skill.id)
        return skill

    def _load_or_create_skill(self, name: str, description: str, files: dict[str, str]) -> Skill:
        existing = self._find_space_skill(name)
        if existing is not None:
            return existing
        return self._ensure_skill(name, description, files)

    def _ensure_skill_set(self) -> _SkillRefs:
        shared = self._load_or_create_skill(
            name="arc-shared-patterns",
            description="Cross-game ARC-AGI-3 heuristics and anti-patterns",
            files={
                "SKILL.md": (
                    "name: arc-shared-patterns\n"
                    "description: Cross-game ARC-AGI-3 heuristics and anti-patterns\n"
                ),
                "cross_game_patterns.md": self.SHARED_TEMPLATE,
            },
        )
        game = self._load_or_create_skill(
            name=f"arc-game-{self.game_id}",
            description=f"Per-game ARC-AGI-3 memory bundle for {self.game_id}",
            files={
                "SKILL.md": (
                    f"name: arc-game-{self.game_id}\n"
                    f"description: Per-game ARC-AGI-3 memory bundle for {self.game_id}\n"
                ),
                "game_mechanic.md": self.MECHANIC_TEMPLATE.format(game_id=self.game_id),
                "failure_log.md": self.FAILURE_TEMPLATE.format(game_id=self.game_id),
                "strategy.md": self.STRATEGY_TEMPLATE.format(game_id=self.game_id, level=0, actions=0),
            },
        )
        verified = self._ensure_verified_skill()
        return _SkillRefs(shared=shared, game=game, verified=verified)

    def _ensure_verified_skill(self) -> Skill | None:
        if self.public_knowledge is None:
            return None
        verified_md = self.public_knowledge.render_markdown(self.game_id)
        summary = self.public_knowledge.get(self.game_id)
        if verified_md is None or summary is None:
            return None
        return self._ensure_skill(
            name=f"arc-verified-{summary.game_id}",
            description=f"Organizer-derived verified summary for public game {summary.game_id}",
            files={
                "SKILL.md": (
                    f"name: arc-verified-{summary.game_id}\n"
                    f"description: Organizer-derived verified summary for public game {summary.game_id}\n"
                ),
                "verified_public.md": verified_md,
            },
        )

    def _read_skill_file(self, skill: Skill, path: str) -> str:
        resp = self.client.skills.get_file(skill_id=skill.id, file_path=path)
        return resp.content.raw if resp.content else ""

    def _write_game_files(self, updates: dict[str, str]) -> None:
        current_files = {
            "SKILL.md": self._read_skill_file(self.refs.game, "SKILL.md"),
            "game_mechanic.md": updates.get("game_mechanic.md", self.read("game_mechanic.md")),
            "failure_log.md": updates.get("failure_log.md", self.read("failure_log.md")),
            "strategy.md": updates.get("strategy.md", self.read("strategy.md")),
        }
        self.refs.game = self._ensure_skill(
            name=self.refs.game.name,
            description=self.refs.game.description,
            files=current_files,
        )

    def _write_shared_files(self, updates: dict[str, str]) -> None:
        current_files = {
            "SKILL.md": self._read_skill_file(self.refs.shared, "SKILL.md"),
            "cross_game_patterns.md": updates.get("cross_game_patterns.md", self.read_shared()),
        }
        self.refs.shared = self._ensure_skill(
            name=self.refs.shared.name,
            description=self.refs.shared.description,
            files=current_files,
        )

    def read(self, name: str) -> str:
        return self._read_skill_file(self.refs.game, name)

    def write(self, name: str, content: str) -> None:
        self._write_game_files({name: content})

    def read_shared(self) -> str:
        return self._read_skill_file(self.refs.shared, "cross_game_patterns.md")

    def write_shared(self, content: str) -> None:
        self._write_shared_files({"cross_game_patterns.md": content})

    def read_verified(self) -> str:
        if self.refs.verified is None:
            return ""
        return self._read_skill_file(self.refs.verified, "verified_public.md")

    def build_context(self, level: int, actions_taken: int) -> str:
        parts = []
        verified = self.read_verified()
        if verified:
            parts.append(f"=== VERIFIED PUBLIC KNOWLEDGE ===\n{verified}")
        parts.append(f"=== CROSS-GAME KNOWLEDGE ===\n{self.read_shared()}")
        mechanic = self.read("game_mechanic.md")
        if "unknown" not in mechanic or level > 0:
            parts.append(f"=== GAME MECHANIC ===\n{mechanic}")
        strategy = self.read("strategy.md")
        strategy = re.sub(r"Level \d+ - \d+ actions taken", f"Level {level} - {actions_taken} actions taken", strategy)
        parts.append(f"=== CURRENT STRATEGY ===\n{strategy}")
        failures = self.read("failure_log.md")
        if "none yet" not in failures:
            parts.append(f"=== FAILURES TO AVOID ===\n{failures[:600]}")
        return "\n\n".join(parts)

    def _parse_distill_response(self, raw: str) -> dict[str, str]:
        mapping = {}
        tags = {
            "mechanic": "game_mechanic.md",
            "failures": "failure_log.md",
            "strategy": "strategy.md",
            "shared": "cross_game_patterns.md",
        }
        for tag, filename in tags.items():
            match = re.search(fr"<{tag}>(.*?)</{tag}>", raw, re.DOTALL)
            if match:
                mapping[filename] = match.group(1).strip()
        return mapping

    def _heuristic_distill(self, episode: list[dict[str, Any]], level: int, win: bool) -> dict[str, str]:
        mechanics = self.read("game_mechanic.md")
        failures = self.read("failure_log.md")
        strategy = self.read("strategy.md")
        shared = self.read_shared()

        no_effect_actions = []
        changed_actions = []
        for step in episode:
            action = step.get("action", "unknown")
            diff = step.get("diff", "")
            if diff == "NO CHANGE":
                no_effect_actions.append(action)
            elif diff and diff != "(first frame)":
                changed_actions.append(f"- {action}: {diff}")

        if changed_actions:
            mechanics = re.sub(
                r"## Discovered Patterns\n.*",
                "## Discovered Patterns\n" + "\n".join(changed_actions[:12]),
                mechanics,
                flags=re.DOTALL,
            )
        if no_effect_actions:
            bullet_block = "\n".join(f"- {action}" for action in sorted(set(no_effect_actions)))
            failures = re.sub(
                r"## Actions With No Effect\n.*",
                "## Actions With No Effect\n" + bullet_block,
                failures,
                flags=re.DOTALL,
            )
        outcome = "WIN" if win else "FAIL"
        strategy = (
            f"# Strategy: {self.game_id} - Level {level + 1}\n\n"
            "## Current Hypothesis\n"
            f"{outcome} after {len(episode)} tracked actions.\n\n"
            "## Next Actions To Try\n"
            "1. Reuse actions that changed the board.\n"
            "2. Avoid actions listed in the failure log unless the frame changes.\n"
            "3. Probe a new coordinate with ACTION6 when the board shows standout cells.\n\n"
            f"## Progress\nLevel {level} - {len(episode)} actions taken\n"
        )
        if changed_actions:
            summary = changed_actions[0].replace("- ", "")
            if summary not in shared:
                shared = shared.rstrip() + f"\n- {summary}"
        return {
            "game_mechanic.md": mechanics,
            "failure_log.md": failures,
            "strategy.md": strategy,
            "cross_game_patterns.md": shared,
        }

    def distill(self, episode: list[dict[str, Any]], level: int, win: bool) -> None:
        if len(episode) < 3:
            return
        session = self.client.sessions.create(
            configs={
                "memory_schema": "arc_agi3",
                "game_id": self.game_id,
                "level": level,
                "win": win,
            }
        )
        self.client.sessions.store_message(
            session.id,
            blob={
                "role": "user",
                "content": json.dumps({"game_id": self.game_id, "level": level, "win": win, "episode": episode}, ensure_ascii=True),
            },
        )

        updates: dict[str, str]
        if self.distill_fn is not None:
            verified = self.read_verified()
            user_content = (
                f"Game={self.game_id} Level={level} Outcome={'WIN' if win else 'FAIL'}\n"
                f"Episode={json.dumps(episode, ensure_ascii=True)}\n\n"
            )
            if verified:
                user_content += f"Verified public knowledge:\n{verified}\n\n"
            user_content += (
                f"Current mechanic:\n{self.read('game_mechanic.md')}\n\n"
                f"Current failures:\n{self.read('failure_log.md')}\n\n"
                f"Current strategy:\n{self.read('strategy.md')}\n\n"
                f"Shared patterns:\n{self.read_shared()}\n"
            )
            prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are a skill extractor for an ARC-AGI-3 game agent. "
                        "Update the provided memory files using only concrete reusable learnings. "
                        "Do not contradict organizer-derived verified public knowledge when it is present. "
                        "Return tags <mechanic>, <failures>, <strategy>, and optional <shared>."
                    ),
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ]
            raw = self.distill_fn(prompt)
            updates = self._parse_distill_response(raw)
            if not updates:
                updates = self._heuristic_distill(episode, level, win)
        else:
            updates = self._heuristic_distill(episode, level, win)

        self._write_game_files(updates)
        if "cross_game_patterns.md" in updates:
            self._write_shared_files(updates)
        self.client.learning_spaces.learn(self.space.id, session_id=session.id)

    def update_shared(self, new_pattern: str) -> None:
        text = self.read_shared()
        if new_pattern.strip() and new_pattern.strip() not in text:
            self.write_shared(text.rstrip() + f"\n- {new_pattern.strip()}")
