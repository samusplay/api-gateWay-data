from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings
import httpx

router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_analytics_dinamico(path: str, request: Request):
    client = request.app.state.http_client
    
    # Apuntamos a la URL del microservicio de analítica
    # ms-analytics usa internamente el prefijo /api/v1/analysis
    target_url = f"{settings.MS_ANALYTICS_URL}/api/v1/analysis/{path}"
    
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    
    try:
        response = await client.request(
            method=request.method,
            url=target_url,
            content=body,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Error: El ms-analytics está apagado o no responde."
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())