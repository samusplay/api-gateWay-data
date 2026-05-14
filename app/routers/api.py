#router
from fastapi import APIRouter

from app.routers import (
    analytics,
    configuration,
    export, 
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
api_router.include_router(export.router)