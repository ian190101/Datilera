from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ReporteDiario,
    AbstractReportesDiariosRepository,
)


class ListarReportesAlumnoIn(BaseModel):
    alumno_id: int = Field(gt=0)
    desde: Optional[date] = None
    hasta: Optional[date] = None


class ListarReportesAlumnoOut(BaseModel):
    reportes: List[ReporteDiario]


class ListarReportesAlumnoCU:
    def __init__(self, reportes_repo: AbstractReportesDiariosRepository) -> None:
        self._reportes_repo = reportes_repo

    async def __call__(
        self,
        data: ListarReportesAlumnoIn,
    ) -> ListarReportesAlumnoOut:
        reportes = await self._reportes_repo.listar_por_alumno(
            alumno_id=data.alumno_id,
            desde=data.desde,
            hasta=data.hasta,
        )
        return ListarReportesAlumnoOut(reportes=reportes)
