"""
GeoRisk AI — FastAPI application entry point.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(
        "GeoRisk AI starting",
        extra={
            "env": settings.app_env,
            "port": settings.app_port,
        },
    )

    # Validate environment configuration.
    settings.validate_environment()

    settings.model_path.mkdir(parents=True, exist_ok=True)
    settings.data_path.mkdir(parents=True, exist_ok=True)

    yield

    logger.info("GeoRisk AI shutting down")


app = FastAPI(
    title="GeoRisk AI",
    description=(
        "AI-powered geotechnical monitoring and risk analysis system for tunnels and stations. "
        "Detects anomalies, predicts failure probability, and classifies structural risk."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

origins = settings.cors_origins

# Security: avoid wildcard CORS in production.
if settings.app_env == "production" and origins == ["*"]:
    logger.warning("CORS is open in production. Consider restricting allowed origins.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
        },
    )

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

# Root endpoint used by basic checks, tests, and load balancers.
@app.get("/", tags=["Root"])
def root():
    return {"message": "GeoRisk AI running"}

app.include_router(router, prefix="")
