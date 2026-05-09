from fastapi import APIRouter, Request

router = APIRouter()

# 🔥 GET perfiles
@router.get("/profiles/")
async def get_profiles(request: Request):
    response = await request.app.state.http_client.get(
        "http://ms-configuration:8000/api/v1/configuration/profiles/"
    )
    return response.json()


# 🔥 POST perfil
@router.post("/profiles/")
async def create_profile(request: Request):
    body = await request.json()

    response = await request.app.state.http_client.post(
        "http://ms-configuration:8000/api/v1/configuration/profiles/",
        json=body
    )
    return response.json()


# 🔥 PUT perfil
@router.put("/profiles/{profile_id}")
async def update_profile(profile_id: int, request: Request):
    body = await request.json()

    response = await request.app.state.http_client.put(
        f"http://ms-configuration:8000/api/v1/configuration/profiles/{profile_id}",
        json=body
    )
    return response.json()


# 🔥 DELETE perfil
@router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: int, request: Request):
    response = await request.app.state.http_client.delete(
        f"http://ms-configuration:8000/api/v1/configuration/profiles/{profile_id}"
    )
    return response.json()