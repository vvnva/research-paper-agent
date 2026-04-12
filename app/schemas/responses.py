from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str
    redis_enabled: bool
    redis_ready: bool


class TelegramWebhookResponse(BaseModel):
    status: str
