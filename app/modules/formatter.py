from __future__ import annotations

from app.schemas.domain import PipelineResult


class ResponseFormatter:
    def format(self, result: PipelineResult) -> str:
        if not result.papers:
            return "Ничего не нашёл по этому запросу. Попробуй уточнить тему или добавить более конкретные термины."

        lines = [f"Запрос: {result.normalized_query}", "", result.message, ""]
        for idx, paper in enumerate(result.papers, start=1):
            lines.append(f"{idx}. {paper.title}")
            if paper.published_at:
                lines.append(f"Дата: {paper.published_at}")
            if paper.authors:
                lines.append(f"Авторы: {', '.join(paper.authors[:4])}")
            if paper.summary:
                lines.append(f"Summary: {paper.summary}")
            if paper.relevance_reason:
                lines.append(f"Почему релевантно: {paper.relevance_reason}")
            lines.append(f"URL: {paper.url}")
            lines.append("")

        degraded = []
        if result.flags.rewrite_fallback:
            degraded.append("rewrite")
        if result.flags.ranking_fallback:
            degraded.append("ranking")
        if result.flags.summarization_fallback:
            degraded.append("summarization")
        if degraded:
            lines.append(f"Частичная деградация: {', '.join(degraded)}")
        return "\n".join(lines).strip()
