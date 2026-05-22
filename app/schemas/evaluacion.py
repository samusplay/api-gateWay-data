from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _ensure_iso8601(v: Optional[str]) -> str:
    """Garantiza un string ISO 8601 válido. Si es nulo, vacío o 'None',
    inyecta la fecha/hora actual del sistema como fallback seguro (CA 4)."""
    if not v or v in ("None", "null", ""):
        return datetime.now(timezone.utc).isoformat()
    return v


class ScoreDeterministicoOut(BaseModel):
    zone_name: str
    score_value: float
    rank_position: int
    dataset_id: str
    execution_id: int
    score_calculated_at: str = Field(
        default="",
        description="Fecha ISO 8601 del cálculo del score determinístico"
    )

    @field_validator("score_calculated_at", mode="before")
    @classmethod
    def validate_score_date(cls, v):
        return _ensure_iso8601(v)


class PotencialPredictivoOut(BaseModel):
    potential_value: float
    confidence_score: float
    business_label: str
    color_code: str
    model_reference: str
    prediction_generated_at: str = Field(
        default="",
        description="Fecha ISO 8601 de generación de la predicción ML"
    )

    @field_validator("prediction_generated_at", mode="before")
    @classmethod
    def validate_prediction_date(cls, v):
        return _ensure_iso8601(v)


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
