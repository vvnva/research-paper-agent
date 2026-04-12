from __future__ import annotations

from datetime import datetime, timezone

from app.core.logging import get_logger
from app.schemas.domain import Paper, SessionState


class InMemoryStateStore:
    def __init__(self) -> None:
        self._session: dict[str, SessionState] = {}
        self._cache: dict[str, list[Paper]] = {}
        self.logger = get_logger(__name__)

    async def ping(self) -> bool:
        return True

    async def get_session(self, session_id: str) -> SessionState | None:
        return self._session.get(session_id)

    async def save_session(self, state: SessionState, ttl_sec: int) -> None:
        state.last_interaction_ts = datetime.now(timezone.utc)
        self._session[state.session_id] = state

    async def get_retrieval_cache(self, key: str) -> list[Paper] | None:
        return self._cache.get(key)

    async def set_retrieval_cache(self, key: str, papers: list[Paper], ttl_sec: int) -> None:
        self._cache[key] = papers
