from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.deps import get_container
from app.core.container import ApplicationContainer
from app.core.errors import ValidationError
from app.schemas.requests import SearchRequest, TelegramUpdate
from app.schemas.responses import HealthResponse, ReadyResponse, TelegramWebhookResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse)
async def ready(container: ApplicationContainer = Depends(get_container)) -> ReadyResponse:
    redis_ready = await container.state_store.ping()
    return ReadyResponse(
        status="ok" if redis_ready or not container.settings.redis_enabled else "degraded",
        redis_enabled=container.settings.redis_enabled,
        redis_ready=redis_ready,
    )


@router.post("/search")
async def search(request: SearchRequest, container: ApplicationContainer = Depends(get_container)):
    result = await container.orchestrator.handle_search(request)
    return result.model_dump(mode="json")


@router.post("/webhook/telegram", response_model=TelegramWebhookResponse)
async def telegram_webhook(
    update: TelegramUpdate,
    container: ApplicationContainer = Depends(get_container),
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> TelegramWebhookResponse:
    secret = container.settings.telegram_webhook_secret
    if secret and x_telegram_bot_api_secret_token != secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid webhook secret")

    extracted = update.extract_text_message()
    if extracted is None:
        return TelegramWebhookResponse(status="ignored")

    chat_id, text = extracted
    session_id = f"tg_{chat_id}"
    try:
        result = await container.orchestrator.handle_search(SearchRequest(session_id=session_id, query=text))
        response_text = container.orchestrator.format_result(result)
    except ValidationError as exc:
        response_text = str(exc)

    await container.telegram_client.send_message(chat_id=chat_id, text=response_text)
    return TelegramWebhookResponse(status="ok")
