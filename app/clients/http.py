from __future__ import annotations

import httpx


class HttpClientFactory:
    @staticmethod
    def build(timeout_sec: float) -> httpx.AsyncClient:
        return httpx.AsyncClient(
    timeout=httpx.Timeout(timeout_sec),
    follow_redirects=True,
)
