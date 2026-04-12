from __future__ import annotations

import asyncio

from app.clients.llm import LLMClient
from app.core.errors import ExternalServiceError
from app.core.retry import retry_async


class QueryRewriter:
    SYSTEM_PROMPT = (
        "You rewrite academic search queries for arXiv. "
        "Return strict JSON with keys: normalized_query, year_from, category."
    )

    def __init__(self, llm_client: LLMClient, timeout_sec: float, retries: int) -> None:
        self.llm_client = llm_client
        self.timeout_sec = timeout_sec
        self.retries = retries

    async def rewrite(self, query: str) -> dict:
        async def _call() -> dict:
            return await asyncio.wait_for(
                self.llm_client.complete_json(self.SYSTEM_PROMPT, f"Query: {query}"),
                timeout=self.timeout_sec,
            )

        try:
            result = await retry_async(_call, retries=self.retries, retry_on=(ExternalServiceError, TimeoutError))
            return {
                "normalized_query": result.get("normalized_query") or query,
                "year_from": result.get("year_from"),
                "category": result.get("category"),
            }
        except Exception:
            return {
                "normalized_query": query,
                "year_from": None,
                "category": None,
                "fallback": True,
            }
