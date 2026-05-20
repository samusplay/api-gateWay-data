import traceback

from fastapi import APIRouter, Depends, HTTPException, Query, Request
import httpx

from app.application.evaluacion_svc import EvaluacionIntegralService
from app.core.config import settings
from app.infrastructure.adapters import HttpAnalyticsAdapter, HttpMLAdapter
from app.schemas.evaluacion import EvaluacionIntegralResponse

router = APIRouter(prefix="/api/v1/evaluacion-integral", tags=["Evaluación Integral Territorial"])

def get_evaluacion_service(request: Request) -> EvaluacionIntegralService:
    client = request.app.state.http_client
    
    analytics_adapter = HttpAnalyticsAdapter(base_url=settings.MS_ANALYTICS_URL, client=client)
    ml_adapter = HttpMLAdapter(base_url=settings.MS_ML_URL, client=client)
    
    return EvaluacionIntegralService(analytics_port=analytics_adapter, ml_port=ml_adapter)

@router.get("/{zone_code}", response_model=EvaluacionIntegralResponse)
async def evaluar_zona_endpoint(
    zone_code: str,
    dataset_id: str = Query(..., description="UUID del dataset para consultar ranking"),
    service: EvaluacionIntegralService = Depends(get_evaluacion_service)
):
    try:
        evaluacion, analytics_ok, ml_ok = await service.evaluar_zona(
            dataset_id=dataset_id,
            zone_code=zone_code
        )
        
        # Mapeo de entidades de dominio a esquemas Pydantic
        score_data = None
        if evaluacion.score:
            score_data = {
                "zone_name": evaluacion.score.zone_name,
                "score_value": evaluacion.score.score_value,
                "rank_position": evaluacion.score.rank_position,
                "dataset_id": evaluacion.score.dataset_id,
                "execution_id": evaluacion.score.execution_id
            }
            
        prediccion_data = None
        if evaluacion.prediccion:
            prediccion_data = {
                "potential_value": evaluacion.prediccion.potential_value,
                "confidence_score": evaluacion.prediccion.confidence_score,
                "business_label": evaluacion.prediccion.business_label,
                "color_code": evaluacion.prediccion.color_code,
                "model_reference": evaluacion.prediccion.model_reference
            }

        return {
            "success": True,
            "data": {
                "zone_code": evaluacion.zone_code,
                "score_deterministico": score_data,
                "potencial_predictivo": prediccion_data,
                "evaluacion_completa": evaluacion.evaluacion_completa
            },
            "fuentes": {
                "analytics_disponible": analytics_ok,
                "ml_disponible": ml_ok
            }
        }

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503, 
            detail="Error de conexión: Uno o más microservicios territoriales no responden."
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"Fallo en microservicio externo: {str(e)}"
        )
    except Exception as e:
        print("🔥 ERROR CRÍTICO EN EVALUACION ROUTER:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno en el Gateway: {repr(e)}"
        )
