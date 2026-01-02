# app/kernel/application/portafolio/reporte/crear_reporte_diario.py
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ReporteDiario,
    AbstractReportesDiariosRepository,
)


class CrearReporteDiarioIn(BaseModel):
    alumno_id: int = Field(gt=0)
    profesora_id: int = Field(gt=0)
    fecha: date
    resumen: Optional[str] = None


class CrearReporteDiarioOut(BaseModel):
    reporte: ReporteDiario

    model_config = {"from_attributes": True}  # ← ¡¡IMPORTANTE!!


class CrearReporteDiarioCU:
    def __init__(self, reportes_repo: AbstractReportesDiariosRepository) -> None:
        self._reportes_repo = reportes_repo

    # ← CAMBIA __call__ POR execute()
    async def execute(self, data: CrearReporteDiarioIn) -> CrearReporteDiarioOut:
        reporte = await self._reportes_repo.crear_o_actualizar(
            alumno_id=data.alumno_id,
            profesora_id=data.profesora_id,
            fecha=data.fecha,
            resumen=data.resumen,
        )
        return CrearReporteDiarioOut(reporte=reporte)