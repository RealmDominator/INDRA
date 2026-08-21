"""INDRA FastAPI application — Step 5 database foundation only."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.domain import router as domain_router
from app.api.intelligence import router as intelligence_router
from app.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="INDRA API",
    version="0.1.0-step6c",
    description="Local development foundation. Business API routes are planned for later steps.",
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
