# Guía de Pruebas Postman - API Gateway

Esta guía describe cómo probar los endpoints clave expuestos por el API Gateway utilizando Postman. Asegúrate de tener los contenedores Docker en ejecución (`docker compose up -d`).

URL Base Local: `http://localhost:8000`

---

## 1. Healthcheck

Verifica que el API Gateway está en línea.

- **Método**: `GET`
- **URL**: `http://localhost:8000/health`
- **Respuesta Esperada (200 OK)**:
```json
{
  "status": "ok",
  "service": "api-gateway"
}
```

---

## 2. Evaluación Integral (Orquestación BFF)

Este endpoint combina datos determinísticos (Analytics) y predicciones de IA (ML) para una zona específica. También registra automáticamente la consulta en el microservicio de Auditoría.

- **Método**: `GET`
- **URL**: `http://localhost:8000/api/v1/evaluacion-integral/{zone_code}?dataset_id={dataset_id}&strategy={strategy}`
- **Parámetros**:
  - `zone_code` (Path): Código de la zona (ej. `0`).
  - `dataset_id` (Query): UUID del dataset procesado (ej. `57c789d2-f256-4279-b6e7-316bf4b578d3`).
  - `strategy` (Query, Opcional): Modelo a usar (ej. `gradient_boosting`, `random_forest`, `knn`). Por defecto: `gradient_boosting`.
- **Respuesta Esperada (200 OK)**:
```json
{
    "success": true,
    "data": {
        "zone_code": "0",
        "score_deterministico": {
            "zone_name": "ANTIOQUIA",
            "score_value": 0.185,
            "rank_position": 2,
            "dataset_id": "57c789d2-...",
            "execution_id": 19,
            "score_calculated_at": "2026-05-22T00:00:00"
        },
        "potencial_predictivo": {
            "potential_value": 1.0,
            "confidence_score": 0.95,
            "business_label": "Zona de Alta Precisión",
            "color_code": "#059669",
            "model_reference": "gradient_boosting",
            "prediction_generated_at": null
        },
        "evaluacion_completa": true,
        "analytics_disponible": true,
        "ml_disponible": true
    },
    "error": null,
    "trace_id": "uuid-trace-id"
}
```
*Nota: Prueba apagar el contenedor `ms-ml` y verás cómo `ml_disponible` cambia a `false` y `error` muestra un mensaje de degradación elegante, sin devolver código 500.*

---

## 3. Trazabilidad y Auditoría de Eventos

Lista todos los eventos de sistema registrados inmutablemente en el microservicio de auditoría.

- **Método**: `GET`
- **URL**: `http://localhost:8000/api/v1/auditoria/events?limit=50&offset=0`
- **Respuesta Esperada (200 OK)**:
```json
[
    {
        "id": 1,
        "event_type": "EVALUACION_INTEGRAL_CONSULTADA",
        "service_name": "api-gateway",
        "trace_id": "uuid-trace-id",
        "event_summary": "Evaluación integral consultada para zona 0. Fuentes cruzadas: 2.",
        "created_at": "2026-05-22T01:15:00",
        "reference_id": "0",
        "status": "SUCCESS"
    }
]
```

---

## 4. Ejecución Directa de Modelos (ML)

Ejecuta el pipeline de IA para un dataset utilizando un modelo específico.

- **Método**: `POST`
- **URL**: `http://localhost:8000/api/v1/ml/execute/{dataset_id}`
- **Body (JSON)**:
```json
{
    "strategy": "knn"
}
```
- **Respuesta Esperada (200 OK)**:
```json
{
    "success": true,
    "dataset_id": "57c789d2-...",
    "algorithm_used": "knn",
    "execution_time_ms": 46,
    "data": [
        {
            "zone_code": "0",
            "potential_score": 0.8,
            "confidence": 0.92,
            "interpretation": {
                "label": "Alta Viabilidad",
                "business_summary": "..."
            },
            "color_code": "#059669",
            "model_evidence": { ... }
        }
    ]
}
```
