from __future__ import annotations

import httpx

from app.core.logging import get_logger


class TelegramClient:
    def __init__(self, api_base: str, bot_token: str, http_client: httpx.AsyncClient) -> None:
        self.api_base = api_base.rstrip("/")
        self.bot_token = bot_token
        self.http_client = http_client
        self.logger = get_logger(__name__)

    async def send_message(self, chat_id: int, text: str) -> None:
        if not self.bot_token:
            self.logger.warning("telegram_send_skipped", reason="missing_bot_token", chat_id=chat_id)
            return
        url = f"{self.api_base}/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
        response = await self.http_client.post(url, json=payload)
        response.raise_for_status()
