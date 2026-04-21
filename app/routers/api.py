# router principal
from fastapi import APIRouter

from app.routers import ingestion, transform, configuration

api_router = APIRouter()

# rutas existentes
api_router.include_router(ingestion.router)
api_router.include_router(transform.router)

# 🔥 NUEVA RUTA CONFIGURATION
api_router.include_router(
    configuration.router,
    prefix="/api/v1/profiles",
    tags=["Configuration"]
)