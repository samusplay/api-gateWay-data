from typing import Any, Dict, List

import httpx

from app.domain.ports import AnalyticsPort, MLPort


class HttpAnalyticsAdapter(AnalyticsPort):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self.base_url = base_url
        self.client = client 

    async def get_analytics(self, dataset_id: str, zone_codes: List[str]) -> List[Dict[str, Any]]:
        # GET a tu endpoint real con el UUID
        url = f"{self.base_url}/api/v1/analytics/zones/metrics/{dataset_id}"
        response = await self.client.get(url)
        response.raise_for_status()
        
        all_zones = response.json().get("data", [])
        # Filtramos para quedarnos solo con las zonas solicitadas (0, 1, 4, etc.)
        return [z for z in all_zones if str(z.get("zone_code")) in zone_codes]

class HttpMLAdapter(MLPort):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self.base_url = base_url
        self.client = client

    async def get_predictions(self, dataset_id: str, zone_codes: List[str], strategy: str) -> List[Dict[str, Any]]:
        # POST a tu endpoint de ML con el UUID
        url = f"{self.base_url}/api/v1/ml/execute/{dataset_id}"
        payload = {"strategy": strategy}
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        
        all_predictions = response.json().get("data", [])
        # Filtramos las predicciones por zone_code
        return [p for p in all_predictions if str(p.get("zone_code")) in zone_codes]