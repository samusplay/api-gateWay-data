#router
from fastapi import APIRouter

from app.routers import ingestion, transform

api_router=APIRouter()
#rUtas hijas
api_router.include_router(ingestion.router)

#registro de rutas 
api_router.include_router(transform.router)