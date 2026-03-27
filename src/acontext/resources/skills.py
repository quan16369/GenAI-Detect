from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path
from typing import Any, BinaryIO

from ..models import DownloadSkillResp, GetSkillFileResp, ListSkillsOutput, Skill
from ..storage import LocalStore


def _normalize_upload(
    file: tuple[str, BinaryIO | bytes] | tuple[str, BinaryIO | bytes, str] | Any,
) -> tuple[str, bytes]:
    if isinstance(file, tuple):
        name = file[0]
        payload = file[1]
        if hasattr(payload, "read"):
            content = payload.read()
        else:
            content = payload
        if not isinstance(content, bytes):
            raise TypeError("Uploaded skill payload must be bytes.")
        return name, content
    raise TypeError("Local backend expects uploads as tuples containing zip bytes.")


def _parse_skill_metadata(skill_md: str, default_name: str) -> tuple[str, str]:
    name_match = re.search(r"^name:\s*(.+)$", skill_md, re.MULTILINE)
    desc_match = re.search(r"^description:\s*(.+)$", skill_md, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else default_name
    description = desc_match.group(1).strip() if desc_match else f"Skill bundle {name}"
    return name, description


class SkillsAPI:
    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def create(
        self,
        *,
        file: tuple[str, BinaryIO | bytes] | tuple[str, BinaryIO | bytes, str],
        user: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> Skill:
        name, payload = _normalize_upload(file)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            files: dict[str, str | bytes] = {}
            skill_md = None
            for member in archive.infolist():
                if member.is_dir():
                    continue
                data = archive.read(member.filename)
                if member.filename.lower().endswith("skill.md"):
                    skill_md = data.decode("utf-8")
                    files[member.filename] = skill_md
                else:
                    try:
                        files[member.filename] = data.decode("utf-8")
                    except UnicodeDecodeError:
                        files[member.filename] = data
        skill_name, description = _parse_skill_metadata(skill_md or "", Path(name).stem)
        return self._store.create_or_update_skill(
            name=skill_name,
            description=description,
            files=files,
            user=user,
            meta=meta,
        )

    def create_from_directory(
        self,
        *,
        name: str,
        directory: str | Path,
        description: str,
        user: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> Skill:
        root = Path(directory).expanduser().resolve()
        files: dict[str, str | bytes] = {}
        for path in sorted(root.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(root).as_posix()
            try:
                files[rel] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                files[rel] = path.read_bytes()
        return self._store.create_or_update_skill(
            name=name,
            description=description,
            files=files,
            user=user,
            meta=meta,
        )

    def upsert_files(
        self,
        *,
        name: str,
        description: str,
        files: dict[str, str | bytes],
        skill_id: str | None = None,
        user: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> Skill:
        return self._store.create_or_update_skill(
            name=name,
            description=description,
            files=files,
            skill_id=skill_id,
            user=user,
            meta=meta,
        )

    def list_catalog(self, **_: Any) -> ListSkillsOutput:
        return self._store.list_skills()

    def get(self, skill_id: str) -> Skill:
        return self._store.get_skill(skill_id)

    def delete(self, skill_id: str) -> None:
        raise NotImplementedError("Skill deletion is not implemented in the local backend.")

    def get_file(self, *, skill_id: str, file_path: str, expire: int | None = None) -> GetSkillFileResp:
        del expire
        return self._store.get_skill_file(skill_id=skill_id, file_path=file_path)

    def download(self, *, skill_id: str, path: str) -> DownloadSkillResp:
        return self._store.download_skill(skill_id=skill_id, path=path)
