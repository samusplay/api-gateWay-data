#router
from fastapi import APIRouter

from app.routers import ingestion

api_router=APIRouter()
#rUtas hijas
api_router.include_router(ingestion.router)