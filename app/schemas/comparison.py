from typing import Dict, List, Optional  # <-- añadir Optional

from pydantic import BaseModel, Field, field_validator


class ComparisonRequest(BaseModel):
    dataset_id: str = Field(..., description="UUID del dataset del CSV")
    zone_codes: List[str] = Field(..., min_length=2, max_length=4)
    ml_strategy: str = Field(default="Gradient_Boosting_Optimizer_v1")

    @field_validator("zone_codes")
    @classmethod
    def no_duplicates(cls, v: List[str]) -> List[str]:
        if len(v) != len(set(v)):
            raise ValueError("zone_codes no puede contener duplicados.")
        return v

class DeltaOut(BaseModel):
    metric_name: str
    difference: float
    is_advantage: bool

class CompetitiveAdvantageOut(BaseModel):
    metric_name: str
    delta_vs_second: float

class ZoneOut(BaseModel):
    zone_code: str
    zone_name: str
    analytics_data: Dict[str, float]
    ml_potential: float
    deltas: List[DeltaOut]

class VerdictOut(BaseModel):
    ranking: List[str]
    winner_code: str
    justification_text: str
    main_competitive_advantage: Optional[CompetitiveAdvantageOut] = None  # <-- esto faltaba

class ComparisonResponse(BaseModel):
    success: bool
    data: List[ZoneOut]
    verdict: VerdictOut