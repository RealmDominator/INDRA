"""INDRA FastAPI application — Step 8C full pipeline integration."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.domain import router as domain_router
from app.api.intelligence import router as intelligence_router
from app.api.ingestion import router as ingestion_router
from app.config.settings import get_settings
from app.ingestion.scheduler import start_scheduler, stop_scheduler
from app.providers.factory import create_llm_provider

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize LLM provider and optional ingestion scheduler."""
    app.state.llm_provider = create_llm_provider()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="INDRA API",
    version="0.4.0-step8c",
    description="India Disruption Response Architecture — full event-to-dashboard pipeline.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(domain_router)
app.include_router(intelligence_router)
app.include_router(ingestion_router)

