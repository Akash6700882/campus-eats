from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import JSONResponse

from app.core.deps import DbSession, require_role
from app.models.enums import RoleName
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.report import ReportFormat, ReportPeriod
from app.services.report_service import ReportService

router = APIRouter(tags=["reports"])

RequireAdmin = Depends(require_role(RoleName.ADMIN.value))

_CONTENT_TYPES = {
    ReportFormat.CSV: "text/csv",
    ReportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ReportFormat.PDF: "application/pdf",
}
_EXTENSIONS = {ReportFormat.CSV: "csv", ReportFormat.EXCEL: "xlsx", ReportFormat.PDF: "pdf"}


@router.get("/admin/reports", dependencies=[RequireAdmin])
async def get_report(
    db: DbSession,
    period: ReportPeriod = Query(default=ReportPeriod.WEEKLY),
    export_format: ReportFormat = Query(default=ReportFormat.JSON, alias="format"),
) -> Response:
    report_service = ReportService(AnalyticsRepository(db))
    report = await report_service.build_report(period)

    if export_format == ReportFormat.JSON:
        return JSONResponse(content=report.model_dump(mode="json"))

    renderers = {
        ReportFormat.CSV: report_service.render_csv,
        ReportFormat.EXCEL: report_service.render_excel,
        ReportFormat.PDF: report_service.render_pdf,
    }
    content = renderers[export_format](report)
    filename = f"campus-eats-report-{period.value}-{report.end_date}.{_EXTENSIONS[export_format]}"
    return Response(
        content=content,
        media_type=_CONTENT_TYPES[export_format],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
