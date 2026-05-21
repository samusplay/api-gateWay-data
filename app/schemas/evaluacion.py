from typing import Optional

from pydantic import BaseModel, Field


class ScoreDeterministicoOut(BaseModel):
    zone_name: str
    score_value: float
    rank_position: int
    dataset_id: str
    execution_id: int
    score_calculated_at: Optional[str] = None

class PotencialPredictivoOut(BaseModel):
    potential_value: float
    confidence_score: float
    business_label: str
    color_code: str
    model_reference: str
    prediction_generated_at: Optional[str] = None

class EvaluacionIntegralOut(BaseModel):
    zone_code: str
    score_deterministico: Optional[ScoreDeterministicoOut] = None
    potencial_predictivo: Optional[PotencialPredictivoOut] = None
    evaluacion_completa: bool
    analytics_disponible: bool
    ml_disponible: bool

class EvaluacionIntegralResponse(BaseModel):
    success: bool
    data: Optional[EvaluacionIntegralOut]
    error: Optional[dict] = None
    trace_id: str
