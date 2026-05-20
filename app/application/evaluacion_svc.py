import asyncio
from typing import Tuple

from app.domain.entities import (
    EvaluacionIntegral,
    PotencialPredictivo,
    ScoreDeterministico,
)
from app.domain.ports import AnalyticsPort, MLPort


class EvaluacionIntegralService:
    def __init__(self, analytics_port: AnalyticsPort, ml_port: MLPort):
        self.analytics_port = analytics_port
        self.ml_port = ml_port

    async def evaluar_zona(
        self,
        dataset_id: str,
        zone_code: str,
    ) -> Tuple[EvaluacionIntegral, bool, bool]:
        
        # Variables para controlar el estado de las fuentes
        analytics_ok = False
        ml_ok = False
        
        # Preparar tareas asincronas con timeout de 3 segundos
        async def fetch_score():
            nonlocal analytics_ok
            try:
                result = await asyncio.wait_for(
                    self.analytics_port.get_zone_score(dataset_id, zone_code),
                    timeout=3.0
                )
                analytics_ok = True
                return result
            except Exception as e:
                print(f"⚠️ Error o timeout al obtener score para zona {zone_code}: {e}")
                return None

        async def fetch_prediction():
            nonlocal ml_ok
            try:
                result = await asyncio.wait_for(
                    self.ml_port.get_zone_prediction(zone_code),
                    timeout=3.0
                )
                ml_ok = True
                return result
            except Exception as e:
                print(f"⚠️ Error o timeout al obtener predicción para zona {zone_code}: {e}")
                return None

        # Ejecutar peticiones concurrentemente
        score_data, prediction_data = await asyncio.gather(
            fetch_score(),
            fetch_prediction()
        )

        # Construir entidades de dominio si los datos están disponibles
        score_entity = None
        if score_data:
            score_entity = ScoreDeterministico(
                zone_code=str(score_data.get("zone_code", zone_code)),
                zone_name=str(score_data.get("zone_name", f"Zona {zone_code}")),
                score_value=float(score_data.get("score_value", 0.0)),
                rank_position=int(score_data.get("rank_position", 0)),
                dataset_id=str(score_data.get("dataset_id", dataset_id)),
                execution_id=int(score_data.get("execution_id", 0))
            )

        pred_entity = None
        if prediction_data and "prediction" in prediction_data:
            pred = prediction_data.get("prediction", {})
            pred_entity = PotencialPredictivo(
                potential_value=float(pred.get("potential_value", 0.0)),
                confidence_score=float(pred.get("confidence_score", 0.0)),
                business_label=str(pred.get("business_label", "")),
                color_code=str(pred.get("color_code", "")),
                model_reference=str(prediction_data.get("model_reference", ""))
            )

        # Determinar si la evaluación está completa (ambas fuentes respondieron con datos)
        evaluacion_completa = bool(score_entity and pred_entity)

        evaluacion = EvaluacionIntegral(
            zone_code=zone_code,
            score=score_entity,
            prediccion=pred_entity,
            evaluacion_completa=evaluacion_completa
        )

        return evaluacion, analytics_ok, ml_ok
