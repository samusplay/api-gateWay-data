# app/routers/export.py

import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.application.export_report_use_case import ExportReportUseCase
from app.core.config import settings
from app.infrastructure.adapters import (
    HttpAnalyticsAdapter,
    HttpAuditAdapter,
    HttpMLAdapter,
    HttpRecommendationsAdapter,
)

router = APIRouter(prefix="/api/v1/export", tags=["Exportación"])


def get_use_case(request: Request) -> ExportReportUseCase:
    client = request.app.state.http_client
    return ExportReportUseCase(
        analytics_port=HttpAnalyticsAdapter(settings.MS_ANALYTICS_URL, client),
        ml_port=HttpMLAdapter(settings.MS_ML_URL, client),
        recommendations_port=HttpRecommendationsAdapter(settings.MS_RECOMMENDATIONS_URL, client),
        audit_port=HttpAuditAdapter(settings.MS_AUDIT_URL, client),
    )


@router.get("/{dataset_id}")
async def export_report(
    dataset_id: str,
    strategy: str = "default",
    use_case: ExportReportUseCase = Depends(get_use_case),
):
    try:
        csv_bytes, filename = await use_case.execute(
            dataset_id=dataset_id,
            strategy=strategy,
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
                    "message": "Error inesperado durante la exportación",
                },
                "trace_id": str(uuid.uuid4()),
            },
        )

    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )