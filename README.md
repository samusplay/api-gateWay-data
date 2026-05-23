# API Gateway - Plataforma de Analítica Territorial

El API Gateway es el punto único de entrada para todas las peticiones desde el frontend (y clientes externos) hacia el ecosistema de microservicios de la Plataforma de Analítica Territorial. Su propósito es orquestar, enrutar y simplificar la comunicación, aislando a los clientes de la topología de la red interna.

## 🚀 Funcionalidades Principales

1. **Enrutamiento Transparente**: Actúa como proxy inverso hacia los microservicios core (`ms-ingestion`, `ms-transform`, `ms-analytics`, `ms-configuration`, `ms-ml`, `ms-recommendations`, `ms-auditoria`).
2. **Orquestación de Servicios (BFF)**: Agrega múltiples llamadas a microservicios en un único endpoint. Ejemplo: `/api/v1/evaluacion-integral/{zone_code}` que combina respuestas de `ms-analytics` y `ms-ml`.
3. **Auditoría Centralizada**: Intercepta llamadas clave y envía eventos de trazabilidad de forma asíncrona ("fire-and-forget") al microservicio de auditoría (`ms-auditoria`).
4. **Resiliencia y Tolerancia a Fallos**: Implementa degradación elegante. Si un microservicio (como ML) no está disponible, el Gateway retorna los datos parciales disponibles sin colapsar el sistema completo.

## 🏗 Arquitectura

El API Gateway está construido con **FastAPI** y sigue una estructura modular:
- `app/routers/`: Controladores que exponen los endpoints agrupados por dominio.
- `app/application/`: Casos de uso de orquestación (ej. `evaluacion_svc.py`).
- `app/infrastructure/`: Adaptadores HTTP que implementan los puertos para comunicarse con otros microservicios mediante `httpx`.
- `app/domain/`: Puertos e interfaces que definen el contrato con los microservicios.

## ⚙️ Configuración (Variables de Entorno)

El servicio requiere conocer las URLs de los microservicios internos. Estas se configuran en el `.env` (gestionado por Docker Compose):

```env
MS_INGESTION_URL=http://ms-ingestion:8000
MS_TRANSFORM_URL=http://ms-transform:8000
MS_ANALYTICS_URL=http://ms-analytics:8000
MS_CONFIGURATION_URL=http://ms-configuration:8000
MS_ML_URL=http://ms-ml:8000
MS_RECOMMENDATIONS_URL=http://ms-recommendations:8000
MS_AUDITORIA_URL=http://ms-auditoria:8000
```

## 🛠 Comandos de Desarrollo

```bash
# Iniciar localmente (fuera de Docker)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Consulta la [Guía de Pruebas Postman](GUIA_PRUEBAS_POSTMAN.md) para más detalles sobre cómo interactuar con los endpoints expuestos.
