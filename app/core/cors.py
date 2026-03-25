from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def configurar_cors(app: FastAPI):
    """
    Configuración de seguridad CORS para permitir que el Frontend (Next.js) 
    se comunique con este API Gateway sin bloqueos del navegador.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL], # Puerto de Next.js
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )