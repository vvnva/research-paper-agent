from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.container import ApplicationContainer, build_container
from app.core.logging import configure_logging, get_logger
from app.observability.metrics import metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = build_container()
    configure_logging(container.settings.log_level)
    logger = get_logger(__name__)
    await container.startup()
    app.state.container = container
    logger.info("application_started", env=container.settings.app_env)
    try:
        yield
    finally:
        logger.info("application_stopping")
        await container.shutdown()


app = FastAPI(title="Research Paper Agent", lifespan=lifespan)
app.include_router(router)
app.include_router(metrics_router)
