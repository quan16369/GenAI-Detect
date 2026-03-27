from __future__ import annotations

from typing import Any

from ..models import (
    LearningSpace,
    LearningSpaceSession,
    LearningSpaceSkill,
    ListLearningSpacesOutput,
    Skill,
)
from ..storage import LocalStore


class LearningSpacesAPI:
    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def create(self, *, user: str | None = None, meta: dict[str, Any] | None = None) -> LearningSpace:
        return self._store.create_learning_space(user=user, meta=meta)

    def list(self, **_: Any) -> ListLearningSpacesOutput:
        return self._store.list_learning_spaces()

    def get(self, space_id: str) -> LearningSpace:
        return self._store.get_learning_space(space_id)

    def update(self, space_id: str, *, meta: dict[str, Any]) -> LearningSpace:
        return self._store.update_learning_space(space_id, meta)

    def delete(self, space_id: str) -> None:
        raise NotImplementedError("Learning space deletion is not implemented in the local backend.")

    def learn(self, space_id: str, *, session_id: str) -> LearningSpaceSession:
        return self._store.learn_from_session(space_id=space_id, session_id=session_id)

    def get_session(self, space_id: str, *, session_id: str) -> LearningSpaceSession:
        return self._store.get_learning_record(space_id=space_id, session_id=session_id)

    def wait_for_learning(
        self,
        space_id: str,
        *,
        session_id: str,
        timeout: float = 120.0,
        poll_interval: float = 1.0,
    ) -> LearningSpaceSession:
        del timeout, poll_interval
        return self.get_session(space_id, session_id=session_id)

    def list_sessions(self, space_id: str) -> list[LearningSpaceSession]:
        return self._store.list_learning_records(space_id=space_id)

    def include_skill(self, space_id: str, *, skill_id: str) -> LearningSpaceSkill:
        return self._store.include_skill(space_id=space_id, skill_id=skill_id)

    def list_skills(self, space_id: str) -> list[Skill]:
        return self._store.list_space_skills(space_id)

    def exclude_skill(self, space_id: str, *, skill_id: str) -> None:
        self._store.exclude_skill(space_id=space_id, skill_id=skill_id)
