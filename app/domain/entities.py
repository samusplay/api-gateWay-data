from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Representa la diferencia matemática entre métricas de dos zonas (CA 4)
@dataclass
class Delta:
    metric_name: str
    difference: float
    is_advantage: bool

# NUEVO: identifica cuál métrica es la ventaja principal del ganador (CA 4)
@dataclass
class CompetitiveAdvantage:
    metric_name: str
    delta_vs_second: float

# Representa una zona individual ya enriquecida con ambas fuentes
@dataclass
class EnrichedZone:
    zone_code: str
    zone_name: str
    analytics_data: Dict[str, float]
    ml_potential: float
    deltas: List[Delta] = field(default_factory=list)

# Representa el veredicto final generado por el Gateway (CA 5)
@dataclass
class ComparisonVerdict:
    ranking: List[str]
    winner_code: str
    justification_text: str
    main_competitive_advantage: Optional[CompetitiveAdvantage] = None  # NUEVO (CA 4)

# El objeto final que el dominio construye y pasa hacia afuera
@dataclass
class ComparisonAggregate:
    zones: List[EnrichedZone]
    verdict: ComparisonVerdict

@dataclass
class ScoreDeterministico:
    zone_code: str
    zone_name: str
    score_value: float
    rank_position: int
    dataset_id: str
    execution_id: int
    score_calculated_at: Optional[str] = None

@dataclass
class PotencialPredictivo:
    potential_value: float
    confidence_score: float
    business_label: str
    color_code: str
    model_reference: str
    prediction_generated_at: Optional[str] = None

@dataclass
class EvaluacionIntegral:
    zone_code: str
    score: Optional[ScoreDeterministico]
    prediccion: Optional[PotencialPredictivo]
    evaluacion_completa: bool