import asyncio
from typing import Any, Dict, List

import httpx

from app.domain.ports import AnalyticsPort, AuditPort, MLPort, RecommendationsPort


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
        if not zone_codes:
            return all_zones
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

class HttpRecommendationsAdapter(RecommendationsPort):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self.base_url = base_url
        self.client = client

    async def get_recommendations(
        self, dataset_id: str, zone_codes: List[str]
    ) -> List[Dict[str, Any]]:
        # El router de recomendaciones recibe zone_code en la URL, uno por uno
        # igual que get_zone_recommendation que me pasaste
        async def fetch_one(zone_code: str) -> Dict[str, Any]:
            url = f"{self.base_url}/api/v1/recommendations/{dataset_id}/{zone_code}"
            response = await self.client.get(url, timeout=10.0)
            if response.status_code == 404:
                # Zona sin recomendación — no explota, retorna vacío
                return {
                    "zone_code": zone_code,
                    "recommendation_level": None,
                    "top_factors": None,
                }
            response.raise_for_status()
            data = response.json().get("data", {})
            return {
                "zone_code": zone_code,
                "recommendation_level": data.get("recommendation_level"),
                "top_factors": data.get("top_factors"),
            }

        return list(await asyncio.gather(*[fetch_one(zc) for zc in zone_codes]))


# --- NUEVO ---
class HttpAuditAdapter(AuditPort):
    def __init__(self, base_url: str, client: httpx.AsyncClient):
        self.base_url = base_url
        self.client = client

    async def emit_export_event(
        self, trace_id: str, filename: str, record_count: int
    ) -> None:
        # CA 3: fallo silencioso — si auditoria está caído no bloquea la descarga
        try:
            await self.client.post(
                f"{self.base_url}/api/v1/audit/events",
                json={
                    "event_type": "DATA_EXPORT_COMPLETED",
                    "trace_id": trace_id,
                    "event_summary": {
                        "filename": filename,
                        "record_count": record_count,
                    },
                },
                timeout=5.0,
            )
        except Exception:
            pass