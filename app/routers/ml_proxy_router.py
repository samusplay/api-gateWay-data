import httpx
from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings

router = APIRouter(
    prefix="/api/v1/ml",
    tags=["Proxy ML"]
)

@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_ml_dinamico(path: str, request: Request):

    client = request.app.state.http_client

    target_url = f"{settings.MS_ML_URL}/api/v1/ml/{path}"

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
            detail="Error: El ms-ml está apagado o no responde."
        )

    except httpx.HTTPStatusError as e:

        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.json()
        )