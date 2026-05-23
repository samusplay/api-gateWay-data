#Configuracion de CORS
import httpx
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from app.core.cors import configurar_cors
from app.routers.api import api_router


# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=300.0)
    print("🌐 Pool de conexiones HTTPX iniciado correctamente.")
    yield
    await app.state.http_client.aclose()
    print("🛑 Pool de conexiones HTTPX cerrado.")

app=FastAPI(
    title="API Gateway - Analítica Territorial",
    description="Gateway central que orquesta las peticiones hacia los microservicios.",
    version="1.0.0",
    lifespan=lifespan
)
#aplicamos cors
configurar_cors(app)

# Registramos middleware transversal de Trazabilidad
from app.core.middleware import TraceIdMiddleware
app.add_middleware(TraceIdMiddleware)

#registramos rutas globales
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"status: Vivo y respirando "}