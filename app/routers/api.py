#router
from fastapi import APIRouter

from app.routers import ingestion

api_router=APIRouter()

api_router.include_router(ingestion.router)