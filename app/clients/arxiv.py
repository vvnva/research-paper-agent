from __future__ import annotations

from xml.etree import ElementTree as ET

import httpx

from app.core.errors import ExternalServiceError
from app.core.logging import get_logger
from app.core.utils import ATOM_NS, parse_iso_date, safe_find_text
from app.schemas.domain import Paper


class ArxivClient:
    def __init__(self, api_base: str, http_client: httpx.AsyncClient) -> None:
        self.api_base = api_base
        self.http_client = http_client
        self.logger = get_logger(__name__)

    async def search(
        self,
        query: str,
        max_results: int = 10,
        year_from: int | None = None,
        category: str | None = None,
    ) -> list[Paper]:
        search_query = self._build_search_query(query=query, year_from=year_from, category=category)
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        try:
            response = await self.http_client.get(self.api_base, params=params)
            response.raise_for_status()
            return self._parse_feed(response.text)
        except (httpx.HTTPError, ET.ParseError) as exc:
            self.logger.warning("arxiv_search_failed", error=str(exc))
            raise ExternalServiceError("arXiv search failed") from exc

    def _build_search_query(self, query: str, year_from: int | None, category: str | None) -> str:
        terms = [f'all:"{query}"']
        if category:
            terms.append(f"cat:{category}")
        # arXiv API has limited date filtering in raw query syntax; year filtering is applied post-parse.
        return " AND ".join(terms)

    def _parse_feed(self, xml_text: str) -> list[Paper]:
        root = ET.fromstring(xml_text)
        papers: list[Paper] = []
        for entry in root.findall("atom:entry", ATOM_NS):
            paper_id = safe_find_text(entry, "atom:id", ATOM_NS)
            title = safe_find_text(entry, "atom:title", ATOM_NS)
            abstract = safe_find_text(entry, "atom:summary", ATOM_NS)
            published = parse_iso_date(safe_find_text(entry, "atom:published", ATOM_NS))
            authors = [
                safe_find_text(author, "atom:name", ATOM_NS)
                for author in entry.findall("atom:author", ATOM_NS)
                if safe_find_text(author, "atom:name", ATOM_NS)
            ]
            categories = [cat.attrib.get("term", "") for cat in entry.findall("atom:category", ATOM_NS)]
            if not paper_id or not title or not abstract:
                continue
            papers.append(
                Paper(
                    paper_id=paper_id,
                    title=" ".join(title.split()),
                    abstract=" ".join(abstract.split()),
                    authors=authors,
                    published_at=published,
                    categories=[c for c in categories if c],
                    url=paper_id,
                )
            )
        return papers
