from __future__ import annotations

import orjson
from redis.asyncio import Redis

from app.schemas.domain import Paper, SessionState
from app.state.store import InMemoryStateStore


class RedisStateStore(InMemoryStateStore):
    def __init__(self, redis: Redis) -> None:
        super().__init__()
        self.redis = redis

    async def ping(self) -> bool:
        return bool(await self.redis.ping())

    async def get_session(self, session_id: str) -> SessionState | None:
        payload = await self.redis.get(f"session:{session_id}")
        if not payload:
            return None
        return SessionState.model_validate(orjson.loads(payload))

    async def save_session(self, state: SessionState, ttl_sec: int) -> None:
        await self.redis.setex(
            f"session:{state.session_id}",
            ttl_sec,
            orjson.dumps(state.model_dump(mode="json")),
        )

    async def get_retrieval_cache(self, key: str) -> list[Paper] | None:
        payload = await self.redis.get(f"cache:retrieval:{key}")
        if not payload:
            return None
        data = orjson.loads(payload)
        return [Paper.model_validate(item) for item in data]

    async def set_retrieval_cache(self, key: str, papers: list[Paper], ttl_sec: int) -> None:
        await self.redis.setex(
            f"cache:retrieval:{key}",
            ttl_sec,
            orjson.dumps([paper.model_dump(mode="json") for paper in papers]),
        )
