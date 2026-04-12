from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    year_from: int | None = None
    max_results: int | None = None
    category: str | None = None


class SearchRequest(BaseModel):
    session_id: str
    query: str
    filters: SearchFilters = Field(default_factory=SearchFilters)


class TelegramChat(BaseModel):
    id: int


class TelegramUser(BaseModel):
    id: int
    username: str | None = None


class TelegramMessage(BaseModel):
    message_id: int
    text: str | None = None
    chat: TelegramChat
    from_: TelegramUser | None = Field(default=None, alias="from")


class TelegramUpdate(BaseModel):
    update_id: int
    message: TelegramMessage | None = None
    edited_message: TelegramMessage | None = None

    def extract_text_message(self) -> tuple[int, str] | None:
        msg = self.message or self.edited_message
        if not msg or not msg.text:
            return None
        return msg.chat.id, msg.text


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMRequest(BaseModel):
    model: str
    messages: list[LLMMessage]
    temperature: float = 0.0
    response_format: dict[str, Any] | None = None


class LLMChoiceMessage(BaseModel):
    content: str


class LLMChoice(BaseModel):
    message: LLMChoiceMessage


class LLMResponse(BaseModel):
    choices: list[LLMChoice]
