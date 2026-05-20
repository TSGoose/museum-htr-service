from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title="Museum OCR Service",
    description="Async handwritten Russian OCR service for museum cards",
    version=settings.app_version,
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
