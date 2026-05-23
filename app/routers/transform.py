
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
            detail={"success": False, "error": "El servicio de transformación no responde o tardó demasiado (Timeout)."}
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail={"success": False, "error": "El ms-transform (Puerto 8002) está apagado o inaccesible."}
        )
    except httpx.HTTPStatusError as e:
        # Si el ms-transform devuelve un 400 o 422, lo pasamos tal cual al frontend
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())