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
    request: Request,
    dataset_id: str = Query(..., description="UUID del dataset para consultar ranking"),
    service: EvaluacionIntegralService = Depends(get_evaluacion_service)
):
    trace_id = getattr(request.state, "trace_id", "unknown-trace-id")
    try:
        evaluacion, analytics_ok, ml_ok = await service.evaluar_zona(
            dataset_id=dataset_id,
            zone_code=zone_code,
            trace_id=trace_id
        )
        
        # Mapeo de entidades de dominio a esquemas Pydantic
        score_data = None
        if evaluacion.score:
            score_data = {
                "zone_name": evaluacion.score.zone_name,
                "score_value": evaluacion.score.score_value,
                "rank_position": evaluacion.score.rank_position,
                "dataset_id": evaluacion.score.dataset_id,
                "execution_id": evaluacion.score.execution_id,
                "score_calculated_at": evaluacion.score.score_calculated_at
            }
            
        prediccion_data = None
        if evaluacion.prediccion:
            prediccion_data = {
                "potential_value": evaluacion.prediccion.potential_value,
                "confidence_score": evaluacion.prediccion.confidence_score,
                "business_label": evaluacion.prediccion.business_label,
                "color_code": evaluacion.prediccion.color_code,
                "model_reference": evaluacion.prediccion.model_reference,
                "prediction_generated_at": evaluacion.prediccion.prediction_generated_at
            }

        # Manejo de alerta si alguna fuente falla (Tolerancia a Fallos Parciales CA 3)
        error_block = None
        if not analytics_ok or not ml_ok:
            fuentes_caidas = []
            if not analytics_ok: fuentes_caidas.append("ms-analytics")
            if not ml_ok: fuentes_caidas.append("ms-ml")
            
            error_block = {
                "code": "PARTIAL_DEGRADATION",
                "message": f"Los siguientes microservicios no respondieron a tiempo o fallaron: {', '.join(fuentes_caidas)}. Se muestran los datos disponibles."
            }

        return {
            "success": True,
            "data": {
                "zone_code": evaluacion.zone_code,
                "score_deterministico": score_data,
                "potencial_predictivo": prediccion_data,
                "evaluacion_completa": evaluacion.evaluacion_completa,
                "analytics_disponible": analytics_ok,
                "ml_disponible": ml_ok
            },
            "error": error_block,
            "trace_id": trace_id
        }

    except Exception as e:
        print("🔥 ERROR CRÍTICO EN EVALUACION ROUTER:")
        traceback.print_exc()
        # CA 3: El BFF jamás debe retornar un Error 500 global, devolvemos un payload estructurado
        return {
            "success": False,
            "data": None,
            "error": {
                "code": "GATEWAY_INTERNAL_ERROR",
                "message": f"Fallo interno en el orquestador: {str(e)}"
            },
            "trace_id": trace_id
        }
