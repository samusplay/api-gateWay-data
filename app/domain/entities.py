from dataclasses import dataclass, field
from typing import Dict, List

""" Lo que se va caragr en memoria ya que no hay bbase de datos"""
# Representa la diferencia matemática entre métricas de dos zonas (CA 4)
@dataclass
class Delta:
    metric_name: str
    difference: float
    is_advantage: bool

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
    ranking: List[str]  # Zonas ordenadas de mejor a peor
    winner_code: str
    justification_text: str

# El objeto final que el dominio construye y pasa hacia afuera
@dataclass
class ComparisonAggregate:
    zones: List[EnrichedZone]
    verdict: ComparisonVerdict