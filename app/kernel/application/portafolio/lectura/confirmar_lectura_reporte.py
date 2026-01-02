# app/kernel/application/portafolio/lectura/confirmar_lectura_reporte.py
from __future__ import annotations

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    LecturaTutor,
    AbstractReportesDiariosRepository,
    AbstractReporteLecturasTutoresRepository,
    ReporteNoEncontradoError,
)


class ConfirmarLecturaReporteIn(BaseModel):
    reporte_id: int = Field(gt=0)
    tutor_id: int = Field(gt=0)


class ConfirmarLecturaReporteOut(BaseModel):
    lectura: LecturaTutor

    model_config = {"from_attributes": True}  # ¡¡Fundamental para serializar ORM!!


class ConfirmarLecturaReporteCU:
    def __init__(
        self,
        reportes_repo: AbstractReportesDiariosRepository,
        lecturas_repo: AbstractReporteLecturasTutoresRepository,
    ) -> None:
        self._reportes_repo = reportes_repo
        self._lecturas_repo = lecturas_repo

    # CAMBIADO: de __call__ → execute
    async def execute(
        self,
        data: ConfirmarLecturaReporteIn,
    ) -> ConfirmarLecturaReporteOut:
        reporte = await self._reportes_repo.obtener_por_id(data.reporte_id)
        if reporte is None:
            raise ReporteNoEncontradoError(reporte_id=data.reporte_id)

        lectura = await self._lecturas_repo.registrar_lectura(
            reporte_id=data.reporte_id,
            tutor_id=data.tutor_id,
        )
        return ConfirmarLecturaReporteOut(lectura=lectura)