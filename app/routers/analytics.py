from fastapi import APIRouter, Request

router = APIRouter()

# ✅ TEST correcto
@router.get("/test")
async def test_analytics(request: Request):
    response = await request.app.state.http_client.get(
        "http://ms-analytics:8000/api/v1/analysis/test"
    )
    return response.json()


# ✅ Ejemplo POST (si luego lo tienes)
@router.post("/run")
async def run_analysis(request: Request):
    body = await request.json()

    response = await request.app.state.http_client.post(
        "http://ms-analytics:8000/api/v1/analysis/run",  # ajusta si existe
        json=body
    )
    return response.json()