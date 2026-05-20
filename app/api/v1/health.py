from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import SessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/ready")
def ready() -> dict:
    settings = get_settings()

    postgres_status = "ok"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        postgres_status = "error"

    segmenter_status = "ok"
    if settings.ocr_segmenter == "kraken" and not settings.ocr_kraken_segmentation_model_path.exists():
        segmenter_status = "model_missing"

    recognizer_status = "ok"
    if settings.ocr_recognizer == "transformers_trocr" and not settings.ocr_trocr_model_path.exists():
        recognizer_status = "will_download_or_use_hf_cache"

    status = "ready" if postgres_status == "ok" and segmenter_status == "ok" else "not_ready"

    return {
        "status": status,
        "postgres": postgres_status,
        "redis": "not_checked",
        "pipeline": settings.ocr_pipeline,
        "segmenter": settings.ocr_segmenter,
        "segmenter_status": segmenter_status,
        "recognizer": settings.ocr_recognizer,
        "recognizer_status": recognizer_status,
    }
