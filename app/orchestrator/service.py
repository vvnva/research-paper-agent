from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from time import perf_counter

from app.core.config import Settings
from app.core.errors import ExternalServiceError, ValidationError
from app.core.logging import get_logger
from app.modules.formatter import ResponseFormatter
from app.modules.ranker import Ranker
from app.modules.retriever import Retriever
from app.modules.rewriter import QueryRewriter
from app.modules.summarizer import Summarizer
from app.modules.validator import InputValidator
from app.observability.metrics import (
    EMPTY_RESULTS_COUNT,
    ERROR_COUNT,
    FALLBACK_COUNT,
    LATENCY_TOTAL,
    REQUEST_COUNT,
    STEP_LATENCY,
    SUCCESS_COUNT,
)
from app.schemas.domain import PipelineFlags, PipelineResult, SessionState
from app.schemas.requests import SearchRequest
from app.state.store import InMemoryStateStore


class ResearchOrchestrator:
    def __init__(
        self,
        settings: Settings,
        validator: InputValidator,
        rewriter: QueryRewriter,
        retriever: Retriever,
        ranker: Ranker,
        summarizer: Summarizer,
        formatter: ResponseFormatter,
        state_store: InMemoryStateStore,
    ) -> None:
        self.settings = settings
        self.validator = validator
        self.rewriter = rewriter
        self.retriever = retriever
        self.ranker = ranker
        self.summarizer = summarizer
        self.formatter = formatter
        self.state_store = state_store
        self.logger = get_logger(__name__)

    async def handle_search(self, request: SearchRequest) -> PipelineResult:
        REQUEST_COUNT.inc()
        started = perf_counter()
        flags = PipelineFlags(degraded_mode=not self.settings.redis_enabled)
        try:
            result = await asyncio.wait_for(
                self._run_pipeline(request=request, flags=flags),
                timeout=self.settings.global_timeout_sec,
            )
            SUCCESS_COUNT.inc()
            LATENCY_TOTAL.observe(perf_counter() - started)
            return result
        except ValidationError:
            ERROR_COUNT.inc()
            LATENCY_TOTAL.observe(perf_counter() - started)
            raise
        except Exception as exc:
            ERROR_COUNT.inc()
            LATENCY_TOTAL.observe(perf_counter() - started)
            self.logger.exception("pipeline_failed", session_id=request.session_id, error=str(exc))
            raise

    async def _run_pipeline(self, request: SearchRequest, flags: PipelineFlags) -> PipelineResult:
        normalized_query = self.validator.validate(request.query)
        session = await self.state_store.get_session(request.session_id)
        effective_filters = request.filters.model_dump(exclude_none=True)

        start = perf_counter()
        rewrite_result = await self.rewriter.rewrite(normalized_query)
        STEP_LATENCY.labels("query_rewrite").observe(perf_counter() - start)
        if rewrite_result.get("fallback"):
            flags.rewrite_fallback = True
            FALLBACK_COUNT.labels("query_rewrite").inc()

        normalized_query = rewrite_result.get("normalized_query") or normalized_query
        year_from = effective_filters.get("year_from") or rewrite_result.get("year_from")
        category = effective_filters.get("category") or rewrite_result.get("category")
        max_results = min(effective_filters.get("max_results") or self.settings.max_candidates, self.settings.max_candidates)

        cache_key = f"{normalized_query}|{year_from}|{category}|{max_results}"
        start = perf_counter()
        papers = await self.state_store.get_retrieval_cache(cache_key)
        if papers is not None:
            flags.retrieval_cache_hit = True
        else:
            try:
                papers = await self.retriever.retrieve(
                    query=normalized_query,
                    max_results=max_results,
                    year_from=year_from,
                    category=category,
                )
                await self.state_store.set_retrieval_cache(cache_key, papers, self.settings.cache_ttl_sec)
            except ExternalServiceError as exc:
                raise ExternalServiceError("retrieval unavailable after retries") from exc
        STEP_LATENCY.labels("retrieval").observe(perf_counter() - start)

        if not papers:
            EMPTY_RESULTS_COUNT.inc()
            await self._save_session(request.session_id, request.query, normalized_query, effective_filters, [])
            return PipelineResult(
                session_id=request.session_id,
                normalized_query=normalized_query,
                papers=[],
                flags=flags,
                message="Результаты не найдены.",
            )

        start = perf_counter()
        ranked, ranking_fallback = await self.ranker.rank(normalized_query, papers)
        STEP_LATENCY.labels("ranking").observe(perf_counter() - start)
        if ranking_fallback:
            flags.ranking_fallback = True
            FALLBACK_COUNT.labels("ranking").inc()

        top_papers = ranked[: self.settings.top_n_results]

        start = perf_counter()
        summarized, summarization_fallback = await self.summarizer.summarize(normalized_query, top_papers)
        STEP_LATENCY.labels("summarization").observe(perf_counter() - start)
        if summarization_fallback:
            flags.summarization_fallback = True
            FALLBACK_COUNT.labels("summarization").inc()

        await self._save_session(
            request.session_id,
            request.query,
            normalized_query,
            {
                **effective_filters,
                **({"year_from": year_from} if year_from else {}),
                **({"category": category} if category else {}),
            },
            [paper.paper_id for paper in summarized],
        )
        return PipelineResult(
            session_id=request.session_id,
            normalized_query=normalized_query,
            papers=summarized,
            flags=flags,
            message=self._build_message(session, flags),
        )

    async def _save_session(
        self,
        session_id: str,
        user_query: str,
        normalized_query: str,
        active_filters: dict,
        last_results: list[str],
    ) -> None:
        state = SessionState(
            session_id=session_id,
            last_user_query=user_query,
            normalized_query=normalized_query,
            active_filters=active_filters,
            last_results=last_results,
            last_interaction_ts=datetime.now(timezone.utc),
        )
        await self.state_store.save_session(state, ttl_sec=self.settings.session_ttl_sec)

    def format_result(self, result: PipelineResult) -> str:
        return self.formatter.format(result)

    @staticmethod
    def _build_message(session: SessionState | None, flags: PipelineFlags) -> str:
        if session is None:
            base = "Ниже — подборка наиболее релевантных статей."
        else:
            base = "Обновил подборку с учётом текущего контекста сессии."
        if flags.retrieval_cache_hit:
            base += " Использован кэш retrieval."
        return base
