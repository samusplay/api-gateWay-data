# app/routers/api.py

from fastapi import APIRouter

from app.routers import (
    analytics,
    comparison,
    configuration,
    export,
    ingestion,
    ml,
    recommendations,
    transform,
    evaluacion,
    auditoria
)

api_router = APIRouter()

# ── Routers con lógica propia (no proxys) — van primero ──
api_router.include_router(comparison.router)
api_router.include_router(export.router)

# ── Proxys — van después ──
api_router.include_router(ingestion.router)
api_router.include_router(transform.router)
api_router.include_router(analytics.router)
api_router.include_router(configuration.router)
api_router.include_router(ml.router)
api_router.include_router(recommendations.router)

# Registro del nuevo Aggregator
api_router.include_router(evaluacion.router)
api_router.include_router(auditoria.router)
