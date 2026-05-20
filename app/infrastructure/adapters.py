from typing import Any, Dict, List, Optional

import httpx

from app.domain.ports import AnalyticsPort, MLPort


class HttpAnalyticsAdapter(AnalyticsPort):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self.base_url = base_url
        self.client = client 

    async def get_analytics(self, dataset_id: str, zone_codes: List[str], trace_id: str = "") -> List[Dict[str, Any]]:
        # GET a tu endpoint real con el UUID
        url = f"{self.base_url}/api/v1/analytics/zones/metrics/{dataset_id}"
        headers = {"X-Trace-Id": trace_id} if trace_id else {}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        
        all_zones = response.json().get("data", [])
        # Filtramos para quedarnos solo con las zonas solicitadas (0, 1, 4, etc.)
        return [z for z in all_zones if str(z.get("zone_code")) in zone_codes]

    async def get_zone_score(self, dataset_id: str, zone_code: str, trace_id: str = "") -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/api/v1/analytics/ranking/{dataset_id}"
        headers = {"X-Trace-Id": trace_id} if trace_id else {}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        zones = data.get("zones", [])
        
        for z in zones:
            if str(z.get("zone_code")) == zone_code:
                return {
                    "zone_code": z.get("zone_code"),
                    "zone_name": z.get("zone_name"),
                    "score_value": z.get("score"),
                    "rank_position": z.get("rank"),
                    "dataset_id": data.get("dataset_id"),
                    "execution_id": data.get("execution_id")
                }
        return None

class HttpMLAdapter(MLPort):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self.base_url = base_url
        self.client = client

    async def get_predictions(self, dataset_id: str, zone_codes: List[str], strategy: str, trace_id: str = "") -> List[Dict[str, Any]]:
        # POST a tu endpoint de ML con el UUID
        url = f"{self.base_url}/api/v1/ml/execute/{dataset_id}"
        payload = {"strategy": strategy}
        headers = {"X-Trace-Id": trace_id} if trace_id else {}
        response = await self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        all_predictions = response.json().get("data", [])
        # Filtramos las predicciones por zone_code
        return [p for p in all_predictions if str(p.get("zone_code")) in zone_codes]

    async def get_zone_prediction(self, zone_code: str, trace_id: str = "") -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/api/v1/ml/predictions/{zone_code}"
        headers = {"X-Trace-Id": trace_id} if trace_id else {}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json().get("data")
        if data:
            return data
        return None