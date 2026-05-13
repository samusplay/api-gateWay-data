#router
from fastapi import APIRouter

from app.routers import (
    analytics,
    comparison,
    configuration,
    ingestion,
    ml,
    recommendations,
    transform,
)

api_router=APIRouter()
#rUtas hijas
api_router.include_router(ingestion.router)

#registro de rutas 
api_router.include_router(transform.router)
api_router.include_router(analytics.router)
api_router.include_router(configuration.router)
api_router.include_router(ml.router)
api_router.include_router(recommendations.router)

# Registro del nuevo Aggregator
api_router.include_router(comparison.router)