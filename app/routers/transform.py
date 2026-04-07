
import httpx
from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings

# 🔹 Usaremos el prefijo /api/v1/transform para mantener el orden de los microservicios
router = APIRouter(prefix="/api/v1/transform", tags=["Proxy Transform"])

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_transform_dinamico(path: str, request: Request):
    client = request.app.state.http_client
    
    # Apuntamos a la URL del microservicio de transformación
    target_url = f"{settings.MS_TRANSFORM_URL}/api/v1/transform/{path}"
    
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
            detail="Error: El ms-transform (Puerto 8002) está apagado o no responde."
        )
    except httpx.HTTPStatusError as e:
        # Si el ms-transform devuelve un 400 o 422, lo pasamos tal cual al frontend
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())