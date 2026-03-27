from __future__ import annotations

import os
from pathlib import Path

from .resources import LearningSpacesAPI, SessionsAPI, SkillsAPI
from .storage import LocalStore


class AcontextClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        storage_dir: str | None = None,
        timeout: float | None = None,
        user_agent: str | None = None,
        client: object | None = None,
    ) -> None:
        del api_key, base_url, timeout, user_agent, client
        root = (
            storage_dir
            or os.getenv("ACONTEXT_STORAGE_DIR")
            or str(Path(".acontext_store").resolve())
        )
        self._store = LocalStore(root)
        self.base_url = f"file://{self._store.root}"
        self.sessions = SessionsAPI(self._store)
        self.skills = SkillsAPI(self._store)
        self.learning_spaces = LearningSpacesAPI(self._store)

    def ping(self) -> str:
        return "pong"

    def close(self) -> None:
        return None

    def __enter__(self) -> "AcontextClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
