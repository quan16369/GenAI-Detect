from __future__ import annotations

import json
import mimetypes
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import (
    DownloadSkillResp,
    FileContent,
    FileInfo,
    GetMessagesOutput,
    GetSkillFileResp,
    LearningSpace,
    LearningSpaceSession,
    LearningSpaceSkill,
    ListLearningSpacesOutput,
    ListSessionsOutput,
    ListSkillsOutput,
    Message,
    Session,
    Skill,
    SkillCatalogItem,
)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id() -> str:
    return str(uuid.uuid4())


class LocalStore:
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        self.sessions_dir = self.root / "sessions"
        self.learning_spaces_dir = self.root / "learning_spaces"
        self.skills_dir = self.root / "skills"
        for path in (self.root, self.sessions_dir, self.learning_spaces_dir, self.skills_dir):
            path.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path, default: Any | None = None) -> Any:
        if not path.exists():
            return {} if default is None else default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _session_dir(self, session_id: str) -> Path:
        return self.sessions_dir / session_id

    def _space_dir(self, space_id: str) -> Path:
        return self.learning_spaces_dir / space_id

    def _skill_dir(self, skill_id: str) -> Path:
        return self.skills_dir / skill_id

    def create_session(
        self,
        *,
        user: str | None = None,
        disable_task_tracking: bool | None = None,
        configs: dict[str, Any] | None = None,
        use_uuid: str | None = None,
    ) -> Session:
        session_id = use_uuid or new_id()
        now = utc_now()
        session = Session(
            id=session_id,
            user=user,
            disable_task_tracking=bool(disable_task_tracking),
            configs=dict(configs or {}),
            created_at=now,
            updated_at=now,
        )
        session_dir = self._session_dir(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(session_dir / "session.json", session.model_dump())
        (session_dir / "messages.jsonl").touch(exist_ok=True)
        return session

    def list_sessions(self) -> ListSessionsOutput:
        items = []
        for session_file in sorted(self.sessions_dir.glob("*/session.json")):
            items.append(Session(**self._read_json(session_file)))
        items.sort(key=lambda item: item.created_at)
        return ListSessionsOutput(items=items, has_more=False)

    def get_session(self, session_id: str) -> Session:
        return Session(**self._read_json(self._session_dir(session_id) / "session.json"))

    def update_session_configs(self, session_id: str, configs: dict[str, Any], *, patch: bool = False) -> Session:
        session = self.get_session(session_id)
        if patch:
            merged = dict(session.configs)
            for key, value in configs.items():
                if value is None:
                    merged.pop(key, None)
                else:
                    merged[key] = value
            session.configs = merged
        else:
            session.configs = dict(configs)
        session.updated_at = utc_now()
        self._write_json(self._session_dir(session_id) / "session.json", session.model_dump())
        return session

    def store_message(
        self,
        session_id: str,
        *,
        blob: dict[str, Any],
        format: str,
        meta: dict[str, Any] | None = None,
    ) -> Message:
        message = Message(
            id=new_id(),
            session_id=session_id,
            format=format,
            blob=dict(blob),
            meta=dict(meta or {}),
            created_at=utc_now(),
        )
        session_dir = self._session_dir(session_id)
        self._append_jsonl(session_dir / "messages.jsonl", message.model_dump())
        session = self.get_session(session_id)
        session.updated_at = message.created_at
        self._write_json(session_dir / "session.json", session.model_dump())
        return message

    def get_messages(self, session_id: str) -> GetMessagesOutput:
        records = [Message(**item) for item in self._read_jsonl(self._session_dir(session_id) / "messages.jsonl")]
        return GetMessagesOutput(
            items=[record.blob for record in records],
            messages=records,
            has_more=False,
        )

    def create_learning_space(self, *, user: str | None = None, meta: dict[str, Any] | None = None) -> LearningSpace:
        space_id = new_id()
        now = utc_now()
        space = LearningSpace(
            id=space_id,
            user=user,
            meta=dict(meta or {}),
            created_at=now,
            updated_at=now,
        )
        space_dir = self._space_dir(space_id)
        space_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(space_dir / "space.json", space.model_dump())
        self._write_json(space_dir / "skill_ids.json", [])
        return space

    def list_learning_spaces(self) -> ListLearningSpacesOutput:
        spaces = []
        for space_file in sorted(self.learning_spaces_dir.glob("*/space.json")):
            spaces.append(LearningSpace(**self._read_json(space_file)))
        spaces.sort(key=lambda item: item.created_at)
        return ListLearningSpacesOutput(items=spaces, has_more=False)

    def get_learning_space(self, space_id: str) -> LearningSpace:
        return LearningSpace(**self._read_json(self._space_dir(space_id) / "space.json"))

    def update_learning_space(self, space_id: str, meta: dict[str, Any]) -> LearningSpace:
        space = self.get_learning_space(space_id)
        merged = dict(space.meta)
        merged.update(meta)
        space.meta = merged
        space.updated_at = utc_now()
        self._write_json(self._space_dir(space_id) / "space.json", space.model_dump())
        return space

    def _skill_meta_path(self, skill_id: str) -> Path:
        return self._skill_dir(skill_id) / "meta.json"

    def _skill_files_dir(self, skill_id: str) -> Path:
        return self._skill_dir(skill_id) / "files"

    def create_or_update_skill(
        self,
        *,
        name: str,
        description: str,
        files: dict[str, str | bytes],
        skill_id: str | None = None,
        user: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> Skill:
        now = utc_now()
        if skill_id is None:
            for existing in self.skills_dir.glob("*/meta.json"):
                current = self._read_json(existing)
                if current.get("name") == name:
                    skill_id = current["id"]
                    break
        skill_id = skill_id or new_id()
        skill_dir = self._skill_dir(skill_id)
        file_root = self._skill_files_dir(skill_id)
        if file_root.exists():
            shutil.rmtree(file_root)
        file_root.mkdir(parents=True, exist_ok=True)

        file_index: list[FileInfo] = []
        for rel_path, content in files.items():
            target = file_root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(content, encoding="utf-8")
            mime = mimetypes.guess_type(str(target))[0] or "text/markdown"
            file_index.append(FileInfo(path=rel_path, mime=mime))

        previous = self._read_json(self._skill_meta_path(skill_id), default={})
        skill = Skill(
            id=skill_id,
            user_id=user or previous.get("user_id"),
            name=name,
            description=description,
            disk_id=f"disk-{skill_id}",
            file_index=sorted(file_index, key=lambda item: item.path),
            meta=dict(meta or previous.get("meta") or {}),
            created_at=previous.get("created_at", now),
            updated_at=now,
        )
        self._write_json(self._skill_meta_path(skill_id), skill.model_dump())
        return skill

    def get_skill(self, skill_id: str) -> Skill:
        raw = self._read_json(self._skill_meta_path(skill_id))
        raw["file_index"] = [FileInfo(**item) for item in raw.get("file_index", [])]
        return Skill(**raw)

    def list_skills(self) -> ListSkillsOutput:
        items = []
        for meta_file in sorted(self.skills_dir.glob("*/meta.json")):
            raw = self._read_json(meta_file)
            items.append(SkillCatalogItem(name=raw["name"], description=raw["description"]))
        items.sort(key=lambda item: item.name.lower())
        return ListSkillsOutput(items=items, has_more=False)

    def get_skill_file(self, *, skill_id: str, file_path: str) -> GetSkillFileResp:
        target = self._skill_files_dir(skill_id) / file_path
        mime = mimetypes.guess_type(str(target))[0] or "text/plain"
        content = None
        if target.exists():
            try:
                content = FileContent(raw=target.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                content = None
        return GetSkillFileResp(path=file_path, mime=mime, content=content)

    def download_skill(self, *, skill_id: str, path: str) -> DownloadSkillResp:
        skill = self.get_skill(skill_id)
        destination = Path(path).expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)
        source = self._skill_files_dir(skill_id)
        files: list[str] = []
        for src in sorted(source.rglob("*")):
            if src.is_dir():
                continue
            rel = src.relative_to(source)
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            files.append(rel.as_posix())
        return DownloadSkillResp(
            name=skill.name,
            description=skill.description,
            dir_path=str(destination),
            files=files,
        )

    def include_skill(self, *, space_id: str, skill_id: str) -> LearningSpaceSkill:
        skill_ids_path = self._space_dir(space_id) / "skill_ids.json"
        skill_ids = self._read_json(skill_ids_path, default=[])
        if skill_id not in skill_ids:
            skill_ids.append(skill_id)
            self._write_json(skill_ids_path, skill_ids)
        stamp = utc_now()
        return LearningSpaceSkill(
            id=new_id(),
            learning_space_id=space_id,
            skill_id=skill_id,
            created_at=stamp,
        )

    def exclude_skill(self, *, space_id: str, skill_id: str) -> None:
        skill_ids_path = self._space_dir(space_id) / "skill_ids.json"
        skill_ids = [item for item in self._read_json(skill_ids_path, default=[]) if item != skill_id]
        self._write_json(skill_ids_path, skill_ids)

    def list_space_skills(self, space_id: str) -> list[Skill]:
        skill_ids = self._read_json(self._space_dir(space_id) / "skill_ids.json", default=[])
        return [self.get_skill(skill_id) for skill_id in skill_ids]

    def get_learning_record(self, *, space_id: str, session_id: str) -> LearningSpaceSession:
        path = self._space_dir(space_id) / "sessions" / f"{session_id}.json"
        return LearningSpaceSession(**self._read_json(path))

    def list_learning_records(self, *, space_id: str) -> list[LearningSpaceSession]:
        records = []
        for path in sorted((self._space_dir(space_id) / "sessions").glob("*.json")):
            records.append(LearningSpaceSession(**self._read_json(path)))
        return records

    def learn_from_session(self, *, space_id: str, session_id: str) -> LearningSpaceSession:
        path = self._space_dir(space_id) / "sessions" / f"{session_id}.json"
        session = self.get_session(session_id)
        if session.configs.get("memory_schema") == "arc_agi3":
            now = utc_now()
            record = LearningSpaceSession(
                id=new_id(),
                session_id=session_id,
                learning_space_id=space_id,
                status="completed",
                created_at=now,
                updated_at=now,
                meta={"mode": "external_arc_distill"},
            )
            self._write_json(path, record.model_dump())
            return record
        messages = self.get_messages(session_id).messages
        bullets: list[str] = []
        for message in messages[-12:]:
            role = message.blob.get("role", "unknown")
            content = str(message.blob.get("content", "")).strip()
            if content:
                bullets.append(f"- {role}: {content[:200]}")
        summary = "\n".join(bullets) or "- Session had no messages."
        skill = self.create_or_update_skill(
            name=f"session-{session.id[:8]}",
            description=f"Auto-distilled transcript summary for session {session.id}",
            files={
                "SKILL.md": (
                    f"name: session-{session.id[:8]}\n"
                    f"description: Auto-distilled transcript summary for session {session.id}\n"
                ),
                "summary.md": (
                    f"# Session Summary\n\n"
                    f"Session ID: {session.id}\n\n"
                    f"## Configs\n{json.dumps(session.configs, indent=2)}\n\n"
                    f"## Messages\n{summary}\n"
                ),
            },
            meta={"source_session_id": session.id, "kind": "session_summary"},
        )
        self.include_skill(space_id=space_id, skill_id=skill.id)
        now = utc_now()
        record = LearningSpaceSession(
            id=new_id(),
            session_id=session_id,
            learning_space_id=space_id,
            status="completed",
            created_at=now,
            updated_at=now,
            meta={"skill_id": skill.id},
        )
        self._write_json(path, record.model_dump())
        return record
