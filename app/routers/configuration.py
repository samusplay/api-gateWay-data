from fastapi import APIRouter, Request

router = APIRouter()

# 🔥 GET perfiles
@router.get("/")
async def get_profiles(request: Request):
    response = await request.app.state.http_client.get(
        "http://ms-configuration:8000/api/v1/profiles/"
    )
    return response.json()


# 🔥 POST perfil
@router.post("/")
async def create_profile(request: Request):
    body = await request.json()

    response = await request.app.state.http_client.post(
        "http://ms-configuration:8000/api/v1/profiles/",
        json=body
    )
    return response.json()


# 🔥 PUT perfil
@router.put("/{profile_id}")
async def update_profile(profile_id: int, request: Request):
    body = await request.json()

    response = await request.app.state.http_client.put(
        f"http://ms-configuration:8000/api/v1/profiles/{profile_id}",
        json=body
    )
    return response.json()