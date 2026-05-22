from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AnalyticsPort(ABC):
    @abstractmethod
    async def get_analytics(self, dataset_id: str, zone_codes: List[str], trace_id: str = "") -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_zone_score(self, dataset_id: str, zone_code: str, trace_id: str = "") -> Optional[Dict[str, Any]]:
        """Obtiene el score y ranking de una zona específica dentro de un dataset."""
        pass

class MLPort(ABC):
    @abstractmethod
    async def get_predictions(self, dataset_id: str, zone_codes: List[str], strategy: str, trace_id: str = "") -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_zone_prediction(self, zone_code: str, trace_id: str = "") -> Optional[Dict[str, Any]]:
        """Obtiene la predicción de potencial de ML para una zona."""
        pass


# --- NUEVO: requerido por CA 1 (consolidar zona con nivel de recomendación) ---
class RecommendationsPort(ABC):
    @abstractmethod
    async def get_recommendations(
        self, dataset_id: str, zone_codes: List[str], trace_id: str = ""
    ) -> List[Dict[str, Any]]:
        pass


# --- NUEVO: requerido por CA 3 (auditoría del evento de consulta) ---
class AuditPort(ABC):
    @abstractmethod
    async def emit_export_event(
        self,
        trace_id: str,
        filename: str,
        record_count: int,
    ) -> None:
        pass