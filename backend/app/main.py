from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.datasets import router as datasets_router
from app.routers.experiments import router as experiments_router
from app.routers.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Dynamic Retail Pricing MAB API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_frontend_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(datasets_router)
    app.include_router(experiments_router)
    return app


def _frontend_origins() -> list[str]:
    configured = os.getenv("FRONTEND_ORIGINS", "")
    origins = [origin.strip() for origin in configured.split(",") if origin.strip()]
    if origins:
        return origins
    return ["http://localhost:5173", "http://127.0.0.1:5173"]


app = create_app()
