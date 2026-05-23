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

        # Si viene "default" o valor vacío, usamos "linear" como valor por defecto seguro
        if not strategy or strategy.lower() == "default":
            strategy = "linear"

        # ── PASO 1: Ranking completo desde ms-analytics ──────────────────────
        try:
            ranking_response = await self.analytics_port.get_ranking(dataset_id=dataset_id)
            zones = ranking_response.get("zones", [])
            executed_at = ranking_response.get("executed_at")
            
            # CA 4: Asignamos el score_calculated_at a cada zona para que aparezca en el CSV
            for z in zones:
                z["score_calculated_at"] = executed_at

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

        # ── PASO 2: ML, Recomendaciones y Métricas Base en paralelo ─────────
        try:
            ml_results, rec_results, metrics_results = await asyncio.gather(
                self.ml_port.get_predictions(
                    dataset_id=dataset_id,
                    zone_codes=zone_codes,
                    strategy=strategy,
                    trace_id=trace_id,
                ),
                self.recommendations_port.get_recommendations(
                    dataset_id=dataset_id,
                    zone_codes=zone_codes,
                    trace_id=trace_id,
                ),
                self.analytics_port.get_analytics(
                    dataset_id=dataset_id,
                    zone_codes=zone_codes,
                    trace_id=trace_id,
                )
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ ERROR ML o Recomendaciones: {type(e).__name__} — {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "success": False,
                    "error": {
                        "code": "AGGREGATION_ERROR",
                        "message": f"No se pudo completar la exportación debido a un error en el servicio de ML o Recomendaciones: {str(e)}",
                    },
                },
            )

        # ── PASO 3: Merge con Pandas ──────────────────────────────────────────
        df_analytics = pd.DataFrame(zones)
        # Flatten predictions for CSV
        flat_ml = []
        for r in ml_results:
            flat_ml.append({
                "zone_code": r.get("zone_code"),
                "potential_value": r.get("prediction", {}).get("potential_value"),
                "confidence_score": r.get("prediction", {}).get("confidence_score"),
                "business_label": r.get("prediction", {}).get("business_label"),
                "model_reference": r.get("model_reference")
            })
        df_ml = pd.DataFrame(flat_ml) if flat_ml else pd.DataFrame()
        df_rec = pd.DataFrame(rec_results)
        df_metrics = pd.DataFrame(metrics_results)

        # Castear todos los zone_code a string para que el merge de pandas funcione
        for df_temp in [df_analytics, df_ml, df_rec, df_metrics]:
            if not df_temp.empty and "zone_code" in df_temp.columns:
                df_temp["zone_code"] = df_temp["zone_code"].astype(str)

        df = (
            df_analytics
            .merge(df_metrics, on="zone_code", how="left")
            .merge(df_ml, on="zone_code", how="left")
            .merge(df_rec, on="zone_code", how="left")
            .drop_duplicates(subset=["zone_code"])
        )

        # Ordenar por zone_code numéricamente si es posible
        df["_sort_key"] = pd.to_numeric(df["zone_code"], errors="coerce")
        df = df.sort_values(by=["_sort_key", "zone_code"]).drop(columns=["_sort_key"])

        # Orden de columnas legible
        ordered_cols = [
            "zone_code",
            "zone_name",
            "poblacion",
            "ingresos",
            "competencia",
            "score",
            "rank",
            "potential_value",
            "recommendation_level",
            "top_factors",
            "score_calculated_at",
            "confidence_score",
            "business_label",
            "prediction_generated_at",
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