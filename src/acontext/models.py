from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ModelMixin:
    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FileContent(ModelMixin):
    raw: str


@dataclass(slots=True)
class FileInfo(ModelMixin):
    path: str
    mime: str


@dataclass(slots=True)
class Skill(ModelMixin):
    id: str
    user_id: str | None
    name: str
    description: str
    disk_id: str
    file_index: list[FileInfo]
    meta: dict[str, Any] | None
    created_at: str
    updated_at: str


@dataclass(slots=True)
class SkillCatalogItem(ModelMixin):
    name: str
    description: str


@dataclass(slots=True)
class ListSkillsOutput(ModelMixin):
    items: list[SkillCatalogItem]
    next_cursor: str | None = None
    has_more: bool = False


@dataclass(slots=True)
class GetSkillFileResp(ModelMixin):
    path: str
    mime: str
    url: str | None = None
    content: FileContent | None = None


@dataclass(slots=True)
class DownloadSkillResp(ModelMixin):
    name: str
    description: str
    dir_path: str
    files: list[str]


@dataclass(slots=True)
class Session(ModelMixin):
    id: str
    user: str | None
    disable_task_tracking: bool
    configs: dict[str, Any]
    created_at: str
    updated_at: str


@dataclass(slots=True)
class Message(ModelMixin):
    id: str
    session_id: str
    format: str
    blob: dict[str, Any]
    meta: dict[str, Any]
    created_at: str


@dataclass(slots=True)
class GetMessagesOutput(ModelMixin):
    items: list[dict[str, Any]]
    messages: list[Message]
    next_cursor: str | None = None
    has_more: bool = False


@dataclass(slots=True)
class ListSessionsOutput(ModelMixin):
    items: list[Session]
    next_cursor: str | None = None
    has_more: bool = False


@dataclass(slots=True)
class LearningSpace(ModelMixin):
    id: str
    user: str | None
    meta: dict[str, Any]
    created_at: str
    updated_at: str


@dataclass(slots=True)
class LearningSpaceSession(ModelMixin):
    id: str
    session_id: str
    learning_space_id: str
    status: str
    created_at: str
    updated_at: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LearningSpaceSkill(ModelMixin):
    id: str
    learning_space_id: str
    skill_id: str
    created_at: str


@dataclass(slots=True)
class ListLearningSpacesOutput(ModelMixin):
    items: list[LearningSpace]
    next_cursor: str | None = None
    has_more: bool = False
