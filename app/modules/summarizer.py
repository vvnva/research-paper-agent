from __future__ import annotations

import asyncio

from app.clients.llm import LLMClient
from app.schemas.domain import Paper


class Summarizer:
    SYSTEM_PROMPT = (
        "You summarize academic papers using only title, abstract, and metadata. "
        "Return strict JSON with key items containing objects: paper_id, summary, relevance_reason."
    )

    def __init__(self, llm_client: LLMClient, timeout_sec: float) -> None:
        self.llm_client = llm_client
        self.timeout_sec = timeout_sec

    async def summarize(self, query: str, papers: list[Paper]) -> tuple[list[Paper], bool]:
        if not papers:
            return [], False
        if not self.llm_client.available:
            return self._fallback(papers), True
        try:
            payload = {
                "query": query,
                "papers": [
                    {
                        "paper_id": p.paper_id,
                        "title": p.title,
                        "abstract": p.abstract[:2000],
                        "published_at": p.published_at,
                        "categories": p.categories,
                    }
                    for p in papers
                ],
            }
            result = await asyncio.wait_for(
                self.llm_client.complete_json(self.SYSTEM_PROMPT, str(payload)),
                timeout=self.timeout_sec,
            )
            items = {item["paper_id"]: item for item in result.get("items", []) if item.get("paper_id")}
            enriched: list[Paper] = []
            for paper in papers:
                item = items.get(paper.paper_id)
                if item:
                    paper.summary = item.get("summary")
                    paper.relevance_reason = item.get("relevance_reason")
                enriched.append(paper)
            return enriched, False
        except Exception:
            return self._fallback(papers), True

    def _fallback(self, papers: list[Paper]) -> list[Paper]:
        for paper in papers:
            paper.summary = None
            paper.relevance_reason = None
        return papers
