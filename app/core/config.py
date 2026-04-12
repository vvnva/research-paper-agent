from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="research-paper-agent", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8080, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_api_base: str = Field(default="https://api.telegram.org", alias="TELEGRAM_API_BASE")
    telegram_webhook_secret: str = Field(default="", alias="TELEGRAM_WEBHOOK_SECRET")

    llm_api_base: str = Field(default="", alias="LLM_API_BASE")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_fallback_model: str = Field(default="", alias="LLM_FALLBACK_MODEL")
    llm_timeout_sec: float = Field(default=5.0, alias="LLM_TIMEOUT_SEC")
    llm_max_retries: int = Field(default=2, alias="LLM_MAX_RETRIES")

    arxiv_api_base: str = Field(default="https://export.arxiv.org/api/query", alias="ARXIV_API_BASE")
    arxiv_timeout_sec: float = Field(default=5.0, alias="ARXIV_TIMEOUT_SEC")
    arxiv_max_retries: int = Field(default=2, alias="ARXIV_MAX_RETRIES")

    global_timeout_sec: float = Field(default=15.0, alias="GLOBAL_TIMEOUT_SEC")
    query_rewrite_timeout_sec: float = Field(default=2.0, alias="QUERY_REWRITE_TIMEOUT_SEC")
    ranking_timeout_sec: float = Field(default=3.0, alias="RANKING_TIMEOUT_SEC")
    summarization_timeout_sec: float = Field(default=5.0, alias="SUMMARIZATION_TIMEOUT_SEC")

    max_candidates: int = Field(default=15, alias="MAX_CANDIDATES")
    top_n_results: int = Field(default=5, alias="TOP_N_RESULTS")
    min_query_len: int = Field(default=5, alias="MIN_QUERY_LEN")
    session_ttl_sec: int = Field(default=3600, alias="SESSION_TTL_SEC")
    cache_ttl_sec: int = Field(default=3600, alias="CACHE_TTL_SEC")

    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    redis_enabled: bool = Field(default=True, alias="REDIS_ENABLED")

    cb_window_sec: int = Field(default=60, alias="CB_WINDOW_SEC")
    cb_failure_rate_threshold: float = Field(default=0.5, alias="CB_FAILURE_RATE_THRESHOLD")
    cb_min_requests: int = Field(default=10, alias="CB_MIN_REQUESTS")
    cb_open_sec: int = Field(default=30, alias="CB_OPEN_SEC")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
