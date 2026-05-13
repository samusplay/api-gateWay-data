import traceback

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

# 1. Importaciones de tu arquitectura
from app.application.comparison_svc import ComparisonService
from app.core.config import settings
from app.infrastructure.adapters import HttpAnalyticsAdapter, HttpMLAdapter
from app.schemas.comparison import ComparisonRequest, ComparisonResponse

router = APIRouter(prefix="/api/v1/comparison", tags=["Comparación Avanzada"])

# Función para inyectar el servicio con el pool de conexiones global
def get_comparison_service(request: Request) -> ComparisonService:
    # Usamos el cliente HTTPX que iniciaste en el lifespan de main.py
    client = request.app.state.http_client
    
    # Adaptadores con las URLs de tus variables de entorno
    analytics_adapter = HttpAnalyticsAdapter(base_url=settings.MS_ANALYTICS_URL, client=client)
    ml_adapter = HttpMLAdapter(base_url=settings.MS_ML_URL, client=client)
    
    return ComparisonService(analytics_port=analytics_adapter, ml_port=ml_adapter)

@router.post("/bulk", response_model=ComparisonResponse)
async def compare_zones_endpoint(
    payload: ComparisonRequest,
    service: ComparisonService = Depends(get_comparison_service)
):
    try:
        # 2. Orquestación: Pasamos el ID del dataset, los códigos y la estrategia
        zones, verdict = await service.compare_zones(
            dataset_id=payload.dataset_id,
            zone_codes=payload.zone_codes,
            ml_strategy=payload.ml_strategy
        )
        
        # 3. Respuesta exitosa estructurada para el Schema
        return {
            "success": True,
            "data": zones,
            "verdict": verdict
        }
    
    # === Bloque de Excepciones Preservado ===
    except httpx.ConnectError:
        # Error si un microservicio está caído (MS_ANALYTICS o MS_ML)
        raise HTTPException(
            status_code=503, 
            detail="Error de conexión: Uno de los microservicios territoriales no responde."
        )
        
    except httpx.HTTPStatusError as e:
        # Error si el microservicio respondió pero con un código de error (400, 404, etc.)
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"Fallo en microservicio externo: {str(e)}"
        )
        
    except Exception as e:
        # 4. Captura de errores internos con impresión de Traceback para depuración
        print("🔥 ERROR CRÍTICO EN COMPARISON ROUTER:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno en el Gateway: {repr(e)}"
        )