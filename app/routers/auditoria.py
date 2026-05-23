import httpx
from fastapi import APIRouter, HTTPException, Query, Request

from app.core.config import settings

router = APIRouter(prefix="/api/v1/auditoria", tags=["Auditoria"])

@router.get("/events")
async def get_audit_events(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Proxy hacia ms-auditoria para obtener el historial de eventos.
    """
    client: httpx.AsyncClient = request.app.state.http_client
    url = f"{settings.MS_AUDITORIA_URL}/api/v1/events"
    
    try:
        response = await client.get(
            url,
            params={"limit": limit, "offset": offset},
            timeout=5.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo conectar con ms-auditoria: {str(e)}"
        )
