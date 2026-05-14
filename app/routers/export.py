import asyncio
import io
from datetime import datetime

import httpx
import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.config import settings

router = APIRouter(prefix="/api/v1/export", tags=["Exportación"])


@router.get("/{dataset_id}")
async def export_report(dataset_id: str, request: Request):
    """
    Orquesta llamadas concurrentes a ms-analytics, ms-ml y ms-recommendations,
    fusiona los datos con Pandas y retorna un CSV descargable.
    """
    client = request.app.state.http_client

    # =====================================================
    # PASO 1: Llamadas concurrentes a los 3 microservicios
    # =====================================================
    async def fetch_analytics():
        try:
            response = await client.get(
                f"{settings.MS_ANALYTICS_URL}/api/v1/analytics/ranking/{dataset_id}",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            raise HTTPException(
                status_code=503,
                detail={"detail": "Error en agregación", "service": "ms-analytics"}
            )

    async def fetch_ml():
        try:
            response = await client.get(
                f"{settings.MS_ML_URL}/api/v1/ml/predictions/{dataset_id}",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            raise HTTPException(
                status_code=503,
                detail={"detail": "Error en agregación", "service": "ms-ml"}
            )

    async def fetch_recommendations():
        try:
            response = await client.get(
                f"{settings.MS_RECOMMENDATIONS_URL}/api/v1/recommendations/{dataset_id}",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            raise HTTPException(
                status_code=503,
                detail={"detail": "Error en agregación", "service": "ms-recommendations"}
            )

    # Ejecutar las 3 llamadas en paralelo
    analytics_data, ml_data, recommendations_data = await asyncio.gather(
        fetch_analytics(),
        fetch_ml(),
        fetch_recommendations()
    )

    # =====================================================
    # PASO 2: Construcción de DataFrames con Pandas
    # =====================================================

    # DataFrame de analytics — zones con score y rank
    df_analytics = pd.DataFrame(analytics_data.get("zones", []))

    # DataFrame de ml — predicciones por zona
    df_ml = pd.DataFrame(ml_data.get("predictions", []))

    # DataFrame de recommendations — recomendaciones por zona
    df_recommendations = pd.DataFrame(recommendations_data.get("recommendations", []))

    # =====================================================
    # PASO 3: Merge por zone_code
    # =====================================================
    if df_analytics.empty:
        raise HTTPException(
            status_code=404,
            detail={"detail": "No hay datos de scoring para exportar", "service": "ms-analytics"}
        )

    # Merge analytics + ml
    df_merged = df_analytics.merge(
        df_ml,
        on="zone_code",
        how="left"  # left join — si ml no tiene datos, no pierde las zonas
    )

    # Merge resultado + recommendations
    df_merged = df_merged.merge(
        df_recommendations,
        on="zone_code",
        how="left"
    )

    # =====================================================
    # PASO 4: Generar CSV en memoria
    # =====================================================
    buffer = io.StringIO()
    df_merged.to_csv(buffer, index=False, encoding="utf-8")
    buffer.seek(0)

    # Nombre del archivo con fecha actual
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"Reporte_Analitico_{today}.csv"

    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )