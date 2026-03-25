import httpx
from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings

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

    try:
        response = await client.request(
            method=request.method,
            url=target_url,
            content=body
        )
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503, 
            detail="Error: El ms-ingestion (Puerto 8001) está apagado o no responde."
        )
    except httpx.HTTPStatusError as e:
        #pasamos al error
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

