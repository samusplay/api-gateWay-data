import asyncio
import io
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.config import settings

router = APIRouter(prefix="/api/v1/export", tags=["Exportación"])


@router.get("/{dataset_id}")
async def export_report(dataset_id: str, request: Request):
    client = request.app.state.http_client

    # =====================================================
    # PASO 1: Obtener ranking desde ms-analytics
    # =====================================================
    try:
        analytics_response = await client.get(
            f"{settings.MS_ANALYTICS_URL}/api/v1/analytics/ranking/{dataset_id}",
            timeout=10.0
        )
        analytics_response.raise_for_status()
        analytics_data = analytics_response.json()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={"detail": "Error en agregación", "service": "ms-analytics"}
        )

    zones = analytics_data.get("zones", [])
    score_calculated_at = analytics_data.get("executed_at", datetime.now().isoformat())

    if not zones:
        raise HTTPException(
            status_code=404,
            detail={"detail": "No hay datos de scoring para exportar", "service": "ms-analytics"}
        )

    # =====================================================
    # PASO 2: Obtener predicciones de ml en paralelo
    # por cada zone_code del ranking
    # =====================================================
    async def fetch_prediction(zone_code: str):
        try:
            response = await client.get(
                f"{settings.MS_ML_URL}/api/v1/ml/predictions/{zone_code}",
                timeout=10.0
            )
            if response.status_code == 404:
                # Si no hay predicción para esa zona retorna vacío
                return {
                    "zone_code": zone_code,
                    "potential_value": None,
                    "confidence_score": None,
                    "business_label": None,
                    "prediction_generated_at": None
                }
            response.raise_for_status()
            data = response.json().get("data", {})
            prediction = data.get("prediction", {})
            return {
                "zone_code": zone_code,
                "potential_value": prediction.get("potential_value"),
                "confidence_score": prediction.get("confidence_score"),
                "business_label": prediction.get("business_label"),
                "prediction_generated_at": data.get("prediction_generated_at")
            }
        except Exception:
            raise HTTPException(
                status_code=503,
                detail={"detail": "Error en agregación", "service": "ms-ml"}
            )

    # Llamadas en paralelo para todas las zonas
    zone_codes = [z["zone_code"] for z in zones]
    predictions = await asyncio.gather(*[fetch_prediction(zc) for zc in zone_codes])

    # =====================================================
    # PASO 3: Construcción de DataFrames y merge
    # =====================================================

    # DataFrame analytics
    df_analytics = pd.DataFrame(zones)
    df_analytics["score_calculated_at"] = score_calculated_at  # CA 4

    # DataFrame ml
    df_ml = pd.DataFrame(predictions)

    # Merge por zone_code — una sola fila por zona
    df_merged = df_analytics.merge(df_ml, on="zone_code", how="left")

    # Eliminar duplicados por si acaso
    df_merged = df_merged.drop_duplicates(subset=["zone_code"])

    # Ordenar columnas para que el CSV sea legible
    columnas = [
        "rank",
        "zone_code",
        "score",
        "score_calculated_at",         # CA 4
        "potential_value",
        "confidence_score",
        "business_label",
        "prediction_generated_at",     # CA 4
    ]
    # Solo incluir columnas que existan en el df
    columnas_existentes = [c for c in columnas if c in df_merged.columns]
    df_merged = df_merged[columnas_existentes]

    # =====================================================
    # PASO 4: Generar CSV en memoria y retornar stream
    # =====================================================
    buffer = io.StringIO()
    df_merged.to_csv(buffer, index=False, encoding="utf-8")
    buffer.seek(0)

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"Reporte_Analitico_{today}.csv"

    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )