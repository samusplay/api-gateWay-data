# app/application/export_report_use_case.py

import asyncio
import io
import uuid
from datetime import datetime
from typing import Tuple

import pandas as pd
from fastapi import HTTPException, status

from app.domain.ports import AnalyticsPort, AuditPort, MLPort, RecommendationsPort


class ExportReportUseCase:
    def __init__(
        self,
        analytics_port: AnalyticsPort,
        ml_port: MLPort,
        recommendations_port: RecommendationsPort,
        audit_port: AuditPort,
    ):
        self.analytics_port = analytics_port
        self.ml_port = ml_port
        self.recommendations_port = recommendations_port
        self.audit_port = audit_port

    async def execute(self, dataset_id: str, strategy: str) -> Tuple[bytes, str]:
        trace_id = str(uuid.uuid4())

        # ── PASO 1: Ranking completo desde ms-analytics ──────────────────────
        # get_analytics retorna todas las zonas, no necesitamos filtrar
        try:
            zones = await self.analytics_port.get_analytics(
                dataset_id=dataset_id,
                zone_codes=[],
            )
        except Exception as e:
            print(f"❌ ERROR Analytics: {type(e).__name__} — {str(e)}")  # ← agregar
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "success": False,
                    "error": {
                        "code": "AGGREGATION_ERROR",
                        "message": "No se pudo completar la exportación debido a un error en el servicio de Analytics",
                    },
                },
            )

        if not zones:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NO_DATA",
                        "message": "No hay datos de scoring para exportar",
                    },
                },
            )

        zone_codes = [str(z["zone_code"]) for z in zones]

        # ── PASO 2: ML y Recomendaciones en paralelo ─────────────────────────
        # CA 2: llamadas concurrentes a los servicios necesarios
        try:
            ml_results, rec_results = await asyncio.gather(
                self.ml_port.get_predictions(
                    dataset_id=dataset_id,
                    zone_codes=zone_codes,
                    strategy=strategy,
                ),
                self.recommendations_port.get_recommendations(
                    dataset_id=dataset_id,
                    zone_codes=zone_codes,
                ),
            )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "success": False,
                    "error": {
                        "code": "AGGREGATION_ERROR",
                        "message": "No se pudo completar la exportación debido a un error en el servicio de ML o Recomendaciones",
                    },
                },
            )

        # ── PASO 3: Merge con Pandas ──────────────────────────────────────────
        # CA 2: usar Pandas para merge de dataframes por zone_code
        # CA 4: score_calculated_at y prediction_generated_at obligatorios
        df_analytics = pd.DataFrame(zones)
        df_ml = pd.DataFrame(ml_results)
        df_rec = pd.DataFrame(rec_results)

        df = (
            df_analytics
            .merge(df_ml, on="zone_code", how="left")
            .merge(df_rec, on="zone_code", how="left")
            .drop_duplicates(subset=["zone_code"])
        )

        # Orden de columnas legible — CA 4 garantiza las dos columnas de temporalidad
        ordered_cols = [
            "rank",
            "zone_code",
            "score",
            "score_calculated_at",       # CA 4
            "potential_value",
            "confidence_score",
            "business_label",
            "prediction_generated_at",   # CA 4
            "recommendation_level",
            "top_factors",
        ]
        df = df[[c for c in ordered_cols if c in df.columns]]

        # ── PASO 4: Serializar a CSV en memoria ───────────────────────────────
        # CA 5: nombre con convención Reporte_Analitico_[Fecha_Actual].csv
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, encoding="utf-8")
        csv_bytes = buffer.getvalue().encode("utf-8")

        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"Reporte_Analitico_{today}.csv"

        # ── PASO 5: Auditoría — CA 3 ──────────────────────────────────────────
        # Fire & forget: si auditoria falla no bloquea la descarga
        await self.audit_port.emit_export_event(
            trace_id=trace_id,
            filename=filename,
            record_count=len(df),
        )

        return csv_bytes, filename