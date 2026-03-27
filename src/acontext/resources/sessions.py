from __future__ import annotations

from typing import Any

from ..models import GetMessagesOutput, ListSessionsOutput, Message, Session
from ..storage import LocalStore


class SessionsAPI:
    def __init__(self, store: LocalStore) -> None:
        self._store = store

    def create(
        self,
        *,
        user: str | None = None,
        disable_task_tracking: bool | None = None,
        configs: dict[str, Any] | None = None,
        use_uuid: str | None = None,
    ) -> Session:
        return self._store.create_session(
            user=user,
            disable_task_tracking=disable_task_tracking,
            configs=configs,
            use_uuid=use_uuid,
        )

    def list(self, **_: Any) -> ListSessionsOutput:
        return self._store.list_sessions()

    def delete(self, session_id: str) -> None:
        raise NotImplementedError("Session deletion is not implemented in the local backend.")

    def update_configs(self, session_id: str, *, configs: dict[str, Any]) -> None:
        self._store.update_session_configs(session_id, configs, patch=False)

    def patch_configs(self, session_id: str, *, configs: dict[str, Any]) -> dict[str, Any]:
        return self._store.update_session_configs(session_id, configs, patch=True).configs

    def get_configs(self, session_id: str) -> Session:
        return self._store.get_session(session_id)

    def store_message(
        self,
        session_id: str,
        *,
        blob: dict[str, Any],
        format: str = "openai",
        meta: dict[str, Any] | None = None,
        file_field: str | None = None,
        file: Any = None,
    ) -> Message:
        if file_field is not None or file is not None:
            raise NotImplementedError("Local backend does not support file uploads in sessions.")
        return self._store.store_message(session_id, blob=blob, format=format, meta=meta)

    def get_messages(
        self,
        session_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        with_asset_public_url: bool | None = None,
        with_events: bool | None = None,
        format: str = "openai",
        time_desc: bool | None = None,
        edit_strategies: list[dict[str, Any]] | None = None,
        pin_editing_strategies_at_message: str | None = None,
    ) -> GetMessagesOutput:
        del limit, cursor, with_asset_public_url, with_events, format, time_desc
        del edit_strategies, pin_editing_strategies_at_message
        return self._store.get_messages(session_id)

    def get_session_summary(self, session_id: str, *, limit: int | None = None) -> str:
        messages = self._store.get_messages(session_id).messages
        if limit is not None:
            messages = messages[:limit]
        chunks = []
        for message in messages:
            role = message.blob.get("role", "unknown")
            content = str(message.blob.get("content", "")).strip()
            if content:
                chunks.append(f"{role}: {content}")
        return "\n".join(chunks)
