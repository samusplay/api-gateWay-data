
from typing import Dict, List

from pydantic import BaseModel, Field

#Le indicamos al frontend que solo nos envie 4 zonas

#Campo que le pasaremos el Request
class ComparisonRequest(BaseModel):
    # Agregamos estos dos campos para que el Router pueda leerlos
    dataset_id: str = Field(..., description="UUID del dataset del CSV")
    zone_codes: List[str] = Field(..., min_length=2, max_length=4)
    ml_strategy: str = Field(default="Gradient_Boosting_Optimizer_v1")

class DeltaOut(BaseModel):
    metric_name: str
    difference: float
    is_advantage: bool

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

class ComparisonResponse(BaseModel):
    success: bool
    data: List[ZoneOut]
    verdict: VerdictOut