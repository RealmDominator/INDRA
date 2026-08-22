"""INDRA FastAPI application — Step 8C full pipeline integration."""
from contextlib import asynccontextmanager
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.domain import router as domain_router
from app.api.intelligence import router as intelligence_router
from app.api.ingestion import router as ingestion_router
from app.config.settings import get_settings
from app.ingestion.scheduler import start_scheduler, stop_scheduler
from app.providers.factory import create_llm_provider

settings = get_settings()
logger = logging.getLogger("indra.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize LLM provider and optional ingestion scheduler."""
    app.state.llm_provider = create_llm_provider()
    logger.info("indra_startup environment=%s ingestion_enabled=%s", settings.app_env, settings.ingestion_enabled)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="INDRA API",
    version="0.4.0-step8c",
    description="India Disruption Response Architecture — full event-to-dashboard pipeline.",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed method=%s path=%s", request.method, request.url.path)
        raise
    logger.info("request_complete method=%s path=%s status=%d duration_ms=%d", request.method, request.url.path, response.status_code, int((time.perf_counter() - started) * 1000))
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_error method=%s path=%s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or [settings.frontend_url],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(health_router)
app.include_router(domain_router)
app.include_router(intelligence_router)
app.include_router(ingestion_router)
