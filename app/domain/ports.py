from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AnalyticsPort(ABC):
    @abstractmethod
    async def get_analytics(self, dataset_id: str, zone_codes: List[str]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_zone_score(self, dataset_id: str, zone_code: str) -> Optional[Dict[str, Any]]:
        """Obtiene el score y ranking de una zona específica dentro de un dataset."""
        pass

class MLPort(ABC):
    @abstractmethod
    async def get_predictions(self, dataset_id: str, zone_codes: List[str], strategy: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_zone_prediction(self, zone_code: str) -> Optional[Dict[str, Any]]:
        """Obtiene la predicción de potencial de ML para una zona."""
        pass