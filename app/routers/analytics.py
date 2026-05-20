import httpx
from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings

router = APIRouter(prefix="/api/v1/analytics", tags=["Proxy Analytics"])

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_analytics_dinamico(path: str, request: Request):
    client = request.app.state.http_client
    
    # Apuntamos a la URL del microservicio de analytics
    target_url = f"{settings.MS_ANALYTICS_URL}/api/v1/analytics/{path}"
    
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    headers["X-Trace-Id"] = getattr(request.state, "trace_id", "")
    
    try:
        response = await client.request(
            method=request.method,
            url=target_url,
            content=body,
            headers=headers,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail={"success": False, "error": "El servicio de analítica no responde o tardó demasiado (Timeout)."}
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail={"success": False, "error": "El ms-analytics (Puerto 8005) está apagado o inaccesible."}
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
