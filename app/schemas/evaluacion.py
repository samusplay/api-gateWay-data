from typing import Optional

from pydantic import BaseModel, Field


class ScoreDeterministicoOut(BaseModel):
    zone_name: str
    score_value: float
    rank_position: int
    dataset_id: str
    execution_id: int

class PotencialPredictivoOut(BaseModel):
    potential_value: float
    confidence_score: float
    business_label: str
    color_code: str
    model_reference: str

class EvaluacionIntegralOut(BaseModel):
    zone_code: str
    score_deterministico: Optional[ScoreDeterministicoOut] = None
    potencial_predictivo: Optional[PotencialPredictivoOut] = None
    evaluacion_completa: bool

class FuentesStatusOut(BaseModel):
    analytics_disponible: bool
    ml_disponible: bool

class EvaluacionIntegralResponse(BaseModel):
    success: bool
    data: EvaluacionIntegralOut
    fuentes: FuentesStatusOut
