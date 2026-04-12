from __future__ import annotations

import asyncio

from app.clients.llm import LLMClient
from app.schemas.domain import Paper


class Ranker:
    SYSTEM_PROMPT = (
        "You rank arXiv papers by relevance to a user query. "
        "Return strict JSON with key ranked_ids containing paper_id list in best-first order."
    )

    def __init__(self, llm_client: LLMClient, timeout_sec: float) -> None:
        self.llm_client = llm_client
        self.timeout_sec = timeout_sec

    async def rank(self, query: str, papers: list[Paper]) -> tuple[list[Paper], bool]:
        if not papers:
            return [], False
        if not self.llm_client.available:
            return papers, True
        try:
            payload = {
                "query": query,
                "papers": [
                    {
                        "paper_id": p.paper_id,
                        "title": p.title,
                        "abstract": p.abstract[:1500],
                        "published_at": p.published_at,
                    }
                    for p in papers
                ],
            }
            result = await asyncio.wait_for(
                self.llm_client.complete_json(self.SYSTEM_PROMPT, str(payload)),
                timeout=self.timeout_sec,
            )
            ids = result.get("ranked_ids") or []
            index = {paper.paper_id: paper for paper in papers}
            ranked = [index[paper_id] for paper_id in ids if paper_id in index]
            leftovers = [paper for paper in papers if paper.paper_id not in set(ids)]
            return ranked + leftovers, False
        except Exception:
            return papers, True
