# app/kernel/application/portafolio/lectura/listar_lecturas_por_reporte.py
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

    # ¡¡ESTO ES OBLIGATORIO para que FastAPI serialice correctamente los objetos ORM!!
    model_config = {"from_attributes": True}


class ListarLecturasPorReporteCU:
    def __init__(
        self,
        lecturas_repo: AbstractReporteLecturasTutoresRepository,
    ) -> None:
        self._lecturas_repo = lecturas_repo

    # CAMBIADO: de __call__ → execute
    async def execute(
        self,
        data: ListarLecturasPorReporteIn,
    ) -> ListarLecturasPorReporteOut:
        lecturas = await self._lecturas_repo.listar_por_reporte(data.reporte_id)
        return ListarLecturasPorReporteOut(lecturas=lecturas)