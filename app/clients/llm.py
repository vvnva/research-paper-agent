from __future__ import annotations

import json

import httpx

from app.core.errors import ExternalServiceError
from app.core.logging import get_logger
from app.schemas.requests import LLMMessage, LLMRequest, LLMResponse


class LLMClient:
    def __init__(self, api_base: str, api_key: str, model: str, http_client: httpx.AsyncClient) -> None:
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.http_client = http_client
        self.logger = get_logger(__name__)

    @property
    def available(self) -> bool:
        return bool(self.api_base and self.api_key and self.model)

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.available:
            raise ExternalServiceError("LLM client is not configured")
        payload = LLMRequest(
            model=self.model,
            messages=[
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt),
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = await self.http_client.post(
                f"{self.api_base}/chat/completions",
                json=payload.model_dump(mode="json"),
                headers=headers,
            )
            response.raise_for_status()
            parsed = LLMResponse.model_validate(response.json())
            content = parsed.choices[0].message.content
            return json.loads(content)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            self.logger.warning("llm_completion_failed", error=str(exc))
            raise ExternalServiceError("LLM completion failed") from exc
