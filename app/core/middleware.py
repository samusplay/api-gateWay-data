import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Intentar extraer de cabeceras, o generar uno nuevo
        trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
        
        # 2. Guardar en el estado de la petición (accesible globalmente durante el ciclo de vida)
        request.state.trace_id = trace_id
        
        # 3. Procesar la petición
        response = await call_next(request)
        
        # 4. Inyectar en la respuesta para el cliente final
        response.headers["X-Trace-Id"] = trace_id
        
        return response
