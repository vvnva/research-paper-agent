from __future__ import annotations

from app.clients.arxiv import ArxivClient
from app.core.errors import ExternalServiceError
from app.core.retry import retry_async
from app.schemas.domain import Paper


class Retriever:
    def __init__(self, arxiv_client: ArxivClient, retries: int) -> None:
        self.arxiv_client = arxiv_client
        self.retries = retries

    async def retrieve(
        self,
        query: str,
        max_results: int,
        year_from: int | None = None,
        category: str | None = None,
    ) -> list[Paper]:
        async def _call() -> list[Paper]:
            return await self.arxiv_client.search(
                query=query,
                max_results=max_results,
                year_from=year_from,
                category=category,
            )

        papers = await retry_async(_call, retries=self.retries, retry_on=(ExternalServiceError,))
        return self._post_process(papers, year_from=year_from)

    def _post_process(self, papers: list[Paper], year_from: int | None = None) -> list[Paper]:
        filtered = []
        seen = set()
        for paper in papers:
            if paper.paper_id in seen:
                continue
            if year_from and paper.published_at and int(paper.published_at[:4]) < year_from:
                continue
            if not paper.title or not paper.abstract:
                continue
            seen.add(paper.paper_id)
            filtered.append(paper)
        return filtered
