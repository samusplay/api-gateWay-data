from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AnalyticsPort(ABC):
    @abstractmethod
    async def get_analytics(self, dataset_id: str, zone_codes: List[str]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_ranking(self, dataset_id: str) -> Dict[str, Any]:
        pass


class MLPort(ABC):
    @abstractmethod
    async def get_predictions(self, dataset_id: str, zone_codes: List[str], strategy: str) -> List[Dict[str, Any]]:
        pass


# --- NUEVO: requerido por CA 1 (consolidar zona con nivel de recomendación) ---
class RecommendationsPort(ABC):
    @abstractmethod
    async def get_recommendations(
        self, dataset_id: str, zone_codes: List[str]
    ) -> List[Dict[str, Any]]:
        pass


# --- NUEVO: requerido por CA 3 (auditoría del evento de exportación) ---
class AuditPort(ABC):
    @abstractmethod
    async def emit_export_event(
        self,
        trace_id: str,
        filename: str,
        record_count: int,
    ) -> None:
        pass