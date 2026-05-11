from fastapi import APIRouter
from app.routers import (
    ingestion,
    transform,
    configuration,
    analytics,
    ml_proxy_router
)

api_router = APIRouter()

api_router.include_router(ingestion.router)
api_router.include_router(transform.router)
api_router.include_router(ml_proxy_router.router)

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