from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AnalyticsPort(ABC):
    @abstractmethod
    async def get_analytics(self, dataset_id: str, zone_codes: List[str]) -> List[Dict[str, Any]]:
        pass

class MLPort(ABC):
    @abstractmethod
    async def get_predictions(self, dataset_id: str, zone_codes: List[str], strategy: str) -> List[Dict[str, Any]]:
        pass