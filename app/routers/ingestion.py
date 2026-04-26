

import httpx
from app.core.config import settings
from fastapi import APIRouter, HTTPException, Request

#todo lo que entre por ingesta
router = APIRouter(prefix="/api/v1/ingesta", tags=["Proxy Ingesta"])

#atrapamos los metodos
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_ingesta_dinamico(path: str, request: Request):
    #traemos el cliente
    client = request.app.state.http_client

    #construir la url
    target_url = f"{settings.MS_INGESTION_URL}/api/v1/ingesta/{path}"

    #leemos el body
    body = await request.body()
    #pasarle los campos
    headers=dict(request.headers)
    headers.pop("host",None)

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
            detail={"success": False, "error": "El servicio de ingesta no responde o tardó demasiado (Timeout)."}
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503, 
            detail={"success": False, "error": "El ms-ingestion (Puerto 8001) está apagado o inaccesible."}
        )
    except httpx.HTTPStatusError as e:
        #pasamos al error
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

