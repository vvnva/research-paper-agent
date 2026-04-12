from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Paper(BaseModel):
    paper_id: str
    title: str
    abstract: str
    authors: list[str] = Field(default_factory=list)
    published_at: str | None = None
    categories: list[str] = Field(default_factory=list)
    url: str
    score: float | None = None
    summary: str | None = None
    relevance_reason: str | None = None


class SessionState(BaseModel):
    session_id: str
    last_user_query: str | None = None
    normalized_query: str | None = None
    active_filters: dict[str, Any] = Field(default_factory=dict)
    last_results: list[str] = Field(default_factory=list)
    last_interaction_ts: datetime | None = None


class PipelineFlags(BaseModel):
    rewrite_fallback: bool = False
    ranking_fallback: bool = False
    summarization_fallback: bool = False
    retrieval_cache_hit: bool = False
    degraded_mode: bool = False


class PipelineResult(BaseModel):
    session_id: str
    normalized_query: str
    papers: list[Paper]
    flags: PipelineFlags = Field(default_factory=PipelineFlags)
    message: str
