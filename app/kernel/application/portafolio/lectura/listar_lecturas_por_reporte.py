from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    LecturaTutor,
    AbstractReporteLecturasTutoresRepository,
)


class ListarLecturasPorReporteIn(BaseModel):
    reporte_id: int = Field(gt=0)


class ListarLecturasPorReporteOut(BaseModel):
    lecturas: List[LecturaTutor]


class ListarLecturasPorReporteCU:
    def __init__(
        self,
        lecturas_repo: AbstractReporteLecturasTutoresRepository,
    ) -> None:
        self._lecturas_repo = lecturas_repo

    async def __call__(
        self,
        data: ListarLecturasPorReporteIn,
    ) -> ListarLecturasPorReporteOut:
        lecturas = await self._lecturas_repo.listar_por_reporte(data.reporte_id)
        return ListarLecturasPorReporteOut(lecturas=lecturas)
