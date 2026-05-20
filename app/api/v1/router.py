from fastapi import APIRouter

from app.api.v1 import corrections, evaluation, health, images, jobs

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(images.router)
api_router.include_router(jobs.router)
api_router.include_router(corrections.router)
api_router.include_router(evaluation.router)
