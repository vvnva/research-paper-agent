from __future__ import annotations

from dataclasses import dataclass

from redis.asyncio import Redis

from app.clients.arxiv import ArxivClient
from app.clients.http import HttpClientFactory
from app.clients.llm import LLMClient
from app.clients.telegram import TelegramClient
from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.modules.formatter import ResponseFormatter
from app.modules.ranker import Ranker
from app.modules.retriever import Retriever
from app.modules.rewriter import QueryRewriter
from app.modules.summarizer import Summarizer
from app.modules.validator import InputValidator
from app.orchestrator.service import ResearchOrchestrator
from app.state.redis_store import RedisStateStore
from app.state.store import InMemoryStateStore


@dataclass
class ApplicationContainer:
    settings: Settings
    telegram_client: TelegramClient
    orchestrator: ResearchOrchestrator
    state_store: InMemoryStateStore
    redis: Redis | None
    llm_circuit_breaker: CircuitBreaker
    arxiv_circuit_breaker: CircuitBreaker
    _http_clients: list

    async def startup(self) -> None:
        logger = get_logger(__name__)
        if self.redis is not None:
            try:
                await self.redis.ping()
                logger.info("redis_ready")
            except Exception as exc:
                logger.warning("redis_unavailable", error=str(exc))
                self.state_store = InMemoryStateStore()
                self.orchestrator.state_store = self.state_store
                self.settings.redis_enabled = False

    async def shutdown(self) -> None:
        for client in self._http_clients:
            await client.aclose()
        if self.redis is not None:
            await self.redis.aclose()


def build_container() -> ApplicationContainer:
    settings = get_settings()

    telegram_http = HttpClientFactory.build(timeout_sec=3.0)
    arxiv_http = HttpClientFactory.build(timeout_sec=settings.arxiv_timeout_sec)
    llm_http = HttpClientFactory.build(timeout_sec=settings.llm_timeout_sec)

    telegram_client = TelegramClient(
        api_base=settings.telegram_api_base,
        bot_token=settings.telegram_bot_token,
        http_client=telegram_http,
    )
    arxiv_client = ArxivClient(settings.arxiv_api_base, arxiv_http)
    llm_client = LLMClient(settings.llm_api_base, settings.llm_api_key, settings.llm_model, llm_http)

    redis = Redis.from_url(settings.redis_url, decode_responses=False) if settings.redis_enabled else None
    state_store = RedisStateStore(redis) if redis is not None else InMemoryStateStore()

    validator = InputValidator(settings)
    rewriter = QueryRewriter(llm_client, settings.query_rewrite_timeout_sec, settings.llm_max_retries)
    retriever = Retriever(arxiv_client, retries=settings.arxiv_max_retries)
    ranker = Ranker(llm_client, settings.ranking_timeout_sec)
    summarizer = Summarizer(llm_client, settings.summarization_timeout_sec)
    formatter = ResponseFormatter()

    orchestrator = ResearchOrchestrator(
        settings=settings,
        validator=validator,
        rewriter=rewriter,
        retriever=retriever,
        ranker=ranker,
        summarizer=summarizer,
        formatter=formatter,
        state_store=state_store,
    )

    cb_config = CircuitBreakerConfig(
        window_sec=settings.cb_window_sec,
        failure_rate_threshold=settings.cb_failure_rate_threshold,
        min_requests=settings.cb_min_requests,
        open_sec=settings.cb_open_sec,
    )

    return ApplicationContainer(
        settings=settings,
        telegram_client=telegram_client,
        orchestrator=orchestrator,
        state_store=state_store,
        redis=redis,
        llm_circuit_breaker=CircuitBreaker(cb_config),
        arxiv_circuit_breaker=CircuitBreaker(cb_config),
        _http_clients=[telegram_http, arxiv_http, llm_http],
    )
