from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class LevelSummary:
    name: str | None
    grid_size: list[int] | None
    data_keys: list[str]


@dataclass(slots=True)
class GameSummary:
    game_id: str
    title: str
    source_path: str
    metadata_path: str
    game_dir_url: str | None
    baseline_actions: list[int]
    level_count: int
    level_names: list[str]
    grid_sizes: list[list[int]]
    level_data_keys: list[str]
    available_actions: list[int | str]
    action_style: str
    clickable_tags: list[str]
    tag_aliases: dict[str, str]
    goal_tags: list[str]
    win_check_tags: list[str]
    step_action_ids: list[int]
    all_tags: list[str]
    line_count: int
    has_hidden_state: bool
    has_custom_valid_actions: bool
    has_next_level: bool
    has_lose: bool
    uses_color_remap: bool
    uses_neighbor_pattern: bool
    uses_renderable_display: bool
    win_method: str | None
    notes: list[str]


@dataclass(slots=True)
class PublicEnvironmentKnowledgeBase:
    games: dict[str, GameSummary]
    aliases: dict[str, str]

    def resolve_game_id(self, game_id: str) -> str | None:
        key = game_id.lower()
        if key in self.aliases:
            return self.aliases[key]
        prefix = key.split("-")[0]
        return self.aliases.get(prefix)

    def get(self, game_id: str) -> GameSummary | None:
        resolved = self.resolve_game_id(game_id)
        if resolved is None:
            return None
        return self.games.get(resolved)

    def render_markdown(self, game_id: str) -> str | None:
        summary = self.get(game_id)
        if summary is None:
            return None
        lines = [
            f"# Verified Public Knowledge: {summary.game_id}",
            "",
            "This section is derived from organizer-provided public environment source code.",
            "Treat it as verified for this public game version only.",
            "",
            f"- Title: `{summary.title}`",
            f"- Source path: `{summary.source_path}`",
            f"- Available actions: `{summary.available_actions}`",
            f"- Action style: `{summary.action_style}`",
            f"- Level count: `{summary.level_count}`",
            f"- Level names: `{summary.level_names}`",
            f"- Grid sizes: `{summary.grid_sizes}`",
            f"- Baseline actions: `{summary.baseline_actions}`",
            f"- Level data keys: `{summary.level_data_keys}`",
            f"- Clickable tags: `{summary.clickable_tags}`",
            f"- Goal tags: `{summary.goal_tags}`",
            f"- Win-check tags: `{summary.win_check_tags}`",
            f"- Win method: `{summary.win_method}`",
            "",
            "## Notes",
        ]
        for note in summary.notes:
            lines.append(f"- {note}")
        return "\n".join(lines)


DEFAULT_REPORT_CANDIDATES = (
    Path("reports/arc_public_env_summary.json"),
    Path(__file__).resolve().parents[2] / "reports" / "arc_public_env_summary.json",
)

DEFAULT_ENV_ROOT_CANDIDATES = (
    Path("arc-prize-2026-arc-agi-3/environment_files"),
    Path("/kaggle/input/competitions/arc-prize-2026-arc-agi-3/environment_files"),
    Path("/kaggle/input/arc-prize-2026-arc-agi-3/environment_files"),
    Path(__file__).resolve().parents[2] / "arc-prize-2026-arc-agi-3" / "environment_files",
)


def _literal(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        value = _literal(node.operand)
        if isinstance(value, (int, float)):
            return -value
    if isinstance(node, ast.List):
        return [_literal(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_literal(item) for item in node.elts)
    if isinstance(node, ast.Dict):
        result: dict[Any, Any] = {}
        for key, value in zip(node.keys, node.values):
            result[_literal(key)] = _literal(value)
        return result
    return None


def _find_assign(tree: ast.AST, name: str) -> ast.Assign | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return node
    return None


def _find_class(tree: ast.AST) -> ast.ClassDef | None:
    for node in tree.body:  # type: ignore[attr-defined]
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "ARCBaseGame":
                    return node
    return None


def _extract_levels(tree: ast.AST) -> list[LevelSummary]:
    assign = _find_assign(tree, "levels")
    if assign is None or not isinstance(assign.value, ast.List):
        return []
    levels: list[LevelSummary] = []
    for element in assign.value.elts:
        if not isinstance(element, ast.Call):
            continue
        if isinstance(element.func, ast.Name) and element.func.id != "Level":
            continue
        name = None
        grid_size = None
        data_keys: list[str] = []
        for kw in element.keywords:
            if kw.arg == "name":
                raw = _literal(kw.value)
                if isinstance(raw, str):
                    name = raw
            elif kw.arg == "grid_size":
                raw = _literal(kw.value)
                if isinstance(raw, tuple):
                    grid_size = [int(v) for v in raw]
            elif kw.arg == "data":
                raw = _literal(kw.value)
                if isinstance(raw, dict):
                    data_keys = sorted(str(key) for key in raw.keys() if isinstance(key, str))
        levels.append(LevelSummary(name=name, grid_size=grid_size, data_keys=data_keys))
    return levels


def _extract_available_actions(class_node: ast.ClassDef) -> list[int | str]:
    for node in ast.walk(class_node):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "__init__":
            continue
        if not isinstance(node.func.value, ast.Call):
            continue
        if not isinstance(node.func.value.func, ast.Name) or node.func.value.func.id != "super":
            continue
        for kw in node.keywords:
            if kw.arg == "available_actions":
                raw = _literal(kw.value)
                if isinstance(raw, list):
                    return raw
    return []


def _extract_method_sources(class_node: ast.ClassDef, source_lines: list[str]) -> dict[str, str]:
    methods: dict[str, str] = {}
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef):
            methods[node.name] = "\n".join(source_lines[node.lineno - 1 : node.end_lineno])
    return methods


def _extract_all_tags(source: str) -> list[str]:
    tags = set()
    for match in re.finditer(r"tags\s*=\s*\[(.*?)\]", source, re.DOTALL):
        tags.update(re.findall(r'"([^"]+)"', match.group(1)))
    return sorted(tags)


def _extract_tag_aliases(source: str) -> dict[str, str]:
    aliases = {}
    for var, tag in re.findall(
        r'self\.(\w+)\s*=\s*self\.current_level\.get_sprites_by_tag\("([^"]+)"\)', source
    ):
        aliases[var] = tag
    return aliases


def _extract_clickable_tags(method_source: str) -> list[str]:
    tags = set(re.findall(r'get_sprites_by_tag\("([^"]+)"\)', method_source))
    tags.update(re.findall(r'get_sprite_at\([^)]*"([^"]+)"\)', method_source))
    return sorted(tags)


def _extract_win_method(step_source: str) -> str | None:
    match = re.search(r"if self\.(\w+)\(\):\s+.*?self\.next_level\(", step_source, re.DOTALL)
    return match.group(1) if match else None


def _action_style(actions: list[int | str]) -> str:
    ints = [value for value in actions if isinstance(value, int)]
    if ints == [6]:
        return "click-only"
    if ints and set(ints).issubset({1, 2, 3, 4, 5}):
        return "button-only"
    if 6 in ints and any(value in {1, 2, 3, 4, 5} for value in ints):
        return "hybrid"
    if not ints:
        return "unknown"
    return "custom"


def _unique_ints(values: list[str]) -> list[int]:
    result = sorted({int(value) for value in values})
    return result


def summarize_environment(game_dir: Path) -> GameSummary:
    metadata_path = game_dir / "metadata.json"
    py_files = sorted(game_dir.glob("*.py"))
    if not py_files:
        raise FileNotFoundError(f"No Python game file found in {game_dir}")
    py_path = py_files[0]

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    source = py_path.read_text(encoding="utf-8")
    source_lines = source.splitlines()
    tree = ast.parse(source)
    class_node = _find_class(tree)
    if class_node is None:
        raise ValueError(f"Could not locate ARCBaseGame subclass in {py_path}")

    levels = _extract_levels(tree)
    methods = _extract_method_sources(class_node, source_lines)
    step_source = methods.get("step", "")
    valid_actions_source = methods.get("_get_valid_actions", "")
    win_method = _extract_win_method(step_source)
    win_source = methods.get(win_method or "", "")
    aliases = _extract_tag_aliases(source)

    goal_tags: list[str] = []
    loop_match = re.search(r"for \w+ in self\.(\w+):", win_source)
    if loop_match:
        alias = loop_match.group(1)
        if alias in aliases:
            goal_tags.append(aliases[alias])

    win_tags = sorted(set(re.findall(r'get_sprite_at\([^)]*"([^"]+)"\)', win_source)))
    clickable_tags = _extract_clickable_tags(valid_actions_source)
    available_actions = _extract_available_actions(class_node)
    step_action_ids = _unique_ints(re.findall(r"self\.action\.id\.value\s*==\s*(\d+)", step_source))
    all_tags = _extract_all_tags(source)
    data_keys = sorted({key for level in levels for key in level.data_keys})
    grid_sizes = [level.grid_size for level in levels if level.grid_size is not None]
    level_names = [level.name for level in levels if level.name]

    has_hidden_state = "_get_hidden_state" in methods
    has_custom_valid_actions = "_get_valid_actions" in methods
    has_next_level = "next_level(" in step_source
    has_lose = "lose(" in step_source
    uses_color_remap = "color_remap(" in step_source
    uses_neighbor_pattern = (
        "range(3)" in step_source
        or "[[0, 0, 0], [0, 1, 0], [0, 0, 0]]" in source
        or "[(-1, -1), (0, -1), (1, -1)]" in step_source
    )
    uses_renderable_display = "RenderableUserDisplay" in source

    notes: list[str] = []
    style = _action_style(available_actions)
    if style == "click-only":
        notes.append("Click-only game: the agent acts through ACTION6 coordinates.")
    elif style == "button-only":
        notes.append("Button-only game: actions appear to use ACTION1-ACTION5 without coordinate clicks.")
    elif style == "hybrid":
        notes.append("Hybrid action space: both button actions and coordinate clicks are available.")
    if clickable_tags:
        notes.append(f"Custom valid-action filtering is present; clickable sprites use tags {clickable_tags}.")
    if uses_color_remap:
        notes.append("Core interaction code remaps sprite colors, suggesting state is encoded by color cycles.")
    if uses_neighbor_pattern:
        notes.append("Step logic uses an explicit neighborhood/pattern mask, indicating local propagation effects.")
    if has_hidden_state and has_lose:
        notes.append("Hidden state plus lose condition suggests a timer, budget, or countdown mechanic.")
    if uses_renderable_display:
        notes.append("Uses a RenderableUserDisplay overlay, likely exposing progress or remaining budget.")
    if win_method:
        target_bits = []
        if goal_tags:
            target_bits.append(f"template/goal sprites tagged {goal_tags}")
        if win_tags:
            target_bits.append(f"board checks against tags {win_tags}")
        suffix = "; ".join(target_bits) if target_bits else "custom win logic"
        notes.append(f"Winning is checked by `{win_method}` using {suffix}.")

    return GameSummary(
        game_id=str(metadata["game_id"]),
        title=str(metadata["title"]),
        source_path=str(py_path),
        metadata_path=str(metadata_path),
        game_dir_url=metadata.get("game_dir_url"),
        baseline_actions=[int(value) for value in metadata.get("baseline_actions", [])],
        level_count=len(levels),
        level_names=level_names,
        grid_sizes=[size for size in grid_sizes if size is not None],
        level_data_keys=data_keys,
        available_actions=available_actions,
        action_style=style,
        clickable_tags=clickable_tags,
        tag_aliases=aliases,
        goal_tags=goal_tags,
        win_check_tags=win_tags,
        step_action_ids=step_action_ids,
        all_tags=all_tags,
        line_count=len(source_lines),
        has_hidden_state=has_hidden_state,
        has_custom_valid_actions=has_custom_valid_actions,
        has_next_level=has_next_level,
        has_lose=has_lose,
        uses_color_remap=uses_color_remap,
        uses_neighbor_pattern=uses_neighbor_pattern,
        uses_renderable_display=uses_renderable_display,
        win_method=win_method,
        notes=notes,
    )


def scan_environment_files(root: Path) -> list[GameSummary]:
    game_dirs = sorted(path.parent for path in root.glob("*/*/metadata.json"))
    return [summarize_environment(game_dir) for game_dir in game_dirs]


def _build_aliases(summaries: list[GameSummary]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    prefix_counts: dict[str, int] = {}
    for summary in summaries:
        exact = summary.game_id.lower()
        aliases[exact] = exact
        aliases[summary.title.lower()] = exact
        prefix = exact.split("-")[0]
        prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
        aliases.setdefault(prefix, exact)
    for prefix, count in prefix_counts.items():
        if count > 1:
            aliases.pop(prefix, None)
    return aliases


def build_public_knowledge_base(summaries: list[GameSummary]) -> PublicEnvironmentKnowledgeBase:
    games = {summary.game_id.lower(): summary for summary in summaries}
    aliases = _build_aliases(summaries)
    return PublicEnvironmentKnowledgeBase(games=games, aliases=aliases)


@lru_cache(maxsize=8)
def load_public_summary_report(json_path: str) -> PublicEnvironmentKnowledgeBase:
    payload = json.loads(Path(json_path).expanduser().resolve().read_text(encoding="utf-8"))
    summaries = [GameSummary(**item) for item in payload["games"]]
    return build_public_knowledge_base(summaries)


@lru_cache(maxsize=8)
def load_public_knowledge_from_environment_root(root: str) -> PublicEnvironmentKnowledgeBase:
    summaries = scan_environment_files(Path(root).expanduser().resolve())
    return build_public_knowledge_base(summaries)


def find_public_knowledge(
    *,
    report_path: str | None = None,
    environment_root: str | None = None,
) -> PublicEnvironmentKnowledgeBase | None:
    if report_path:
        path = Path(report_path).expanduser().resolve()
        if path.exists():
            return load_public_summary_report(str(path))
    if environment_root:
        path = Path(environment_root).expanduser().resolve()
        if path.exists():
            return load_public_knowledge_from_environment_root(str(path))
    for candidate in DEFAULT_REPORT_CANDIDATES:
        path = candidate.expanduser().resolve()
        if path.exists():
            return load_public_summary_report(str(path))
    for candidate in DEFAULT_ENV_ROOT_CANDIDATES:
        path = candidate.expanduser().resolve()
        if path.exists():
            return load_public_knowledge_from_environment_root(str(path))
    return None


def _markdown_report(summaries: list[GameSummary], root: Path) -> str:
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# ARC-AGI-3 Public Environment Summary",
        "",
        f"Generated from `{root}` on `{generated_at}`.",
        "",
        "This report is static analysis over the organizer-provided public environment source files.",
        "The notes are heuristic summaries, not executable proofs.",
        "",
        f"Total public environments: **{len(summaries)}**",
        "",
        "| Game | Title | Actions | Levels | Click Tags | Signals |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for summary in summaries:
        signals = []
        if summary.has_hidden_state:
            signals.append("hidden-state")
        if summary.uses_color_remap:
            signals.append("color-remap")
        if summary.uses_neighbor_pattern:
            signals.append("3x3-pattern")
        if summary.has_custom_valid_actions:
            signals.append("custom-valid-actions")
        if summary.uses_renderable_display:
            signals.append("display-overlay")
        lines.append(
            f"| `{summary.game_id}` | `{summary.title}` | `{summary.available_actions}` | "
            f"{summary.level_count} | `{summary.clickable_tags}` | `{', '.join(signals)}` |"
        )
    lines.append("")
    lines.append("## Per-game Notes")
    lines.append("")
    for summary in summaries:
        lines.append(f"### `{summary.game_id}`")
        lines.append(f"- Source: `{summary.source_path}`")
        lines.append(f"- Levels: {summary.level_count} with names `{summary.level_names}`")
        lines.append(f"- Grid sizes: `{summary.grid_sizes}`")
        lines.append(f"- Metadata baseline actions: `{summary.baseline_actions}`")
        lines.append(f"- Level data keys: `{summary.level_data_keys}`")
        lines.append(f"- Action style: `{summary.action_style}` with `available_actions={summary.available_actions}`")
        lines.append(f"- Clickable tags from `_get_valid_actions`: `{summary.clickable_tags}`")
        lines.append(f"- Goal tags: `{summary.goal_tags}`; win-check tags: `{summary.win_check_tags}`")
        lines.append(f"- Tag aliases from `on_set_level`: `{summary.tag_aliases}`")
        for note in summary.notes:
            lines.append(f"- {note}")
        lines.append("")
    return "\n".join(lines)


def write_reports(summaries: list[GameSummary], json_path: Path, markdown_path: Path, root: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "games": [asdict(summary) for summary in summaries],
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    markdown_path.write_text(_markdown_report(summaries, root), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize ARC-AGI-3 public environment source files.")
    parser.add_argument(
        "--environment-root",
        default="arc-prize-2026-arc-agi-3/environment_files",
        help="Path to the organizer-provided environment_files directory.",
    )
    parser.add_argument(
        "--json-out",
        default="reports/arc_public_env_summary.json",
        help="Output path for the JSON report.",
    )
    parser.add_argument(
        "--markdown-out",
        default="reports/arc_public_env_summary.md",
        help="Output path for the Markdown report.",
    )
    args = parser.parse_args()

    root = Path(args.environment_root).expanduser().resolve()
    summaries = scan_environment_files(root)
    write_reports(summaries, Path(args.json_out), Path(args.markdown_out), root)
    print(f"Wrote {len(summaries)} game summaries to {args.json_out} and {args.markdown_out}")


if __name__ == "__main__":
    main()
