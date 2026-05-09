from fastapi import APIRouter
from app.routers import ingestion, transform, configuration, analytics

api_router = APIRouter()

api_router.include_router(ingestion.router)
api_router.include_router(transform.router)

# ✅ configuration
api_router.include_router(
    configuration.router,
    prefix="/api/v1/configuration",
    tags=["Configuration"]
)

# ✅ analytics
api_router.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)