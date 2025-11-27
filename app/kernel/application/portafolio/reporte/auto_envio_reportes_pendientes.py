from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ReporteDiario,
    AbstractReportesDiariosRepository,
)
from app.kernel.domain.notificaciones.notificaciones import (
    CrearNotificacionInput,
    AbstractNotificacionesService, 
)


class AutoEnvioReportesPendientesIn(BaseModel):
    fecha: date
    mapa_reporte_tutores: Dict[int, List[int]] = Field(default_factory=dict)


class AutoEnvioReportesPendientesOut(BaseModel):
    enviados: List[int]


class AutoEnvioReportesPendientesCU:
    def __init__(
        self,
        reportes_repo: AbstractReportesDiariosRepository,
        notificaciones_service: AbstractNotificacionesService,
    ) -> None:
        self._reportes_repo = reportes_repo
        self._notificaciones_service = notificaciones_service

    async def __call__(
        self,
        data: AutoEnvioReportesPendientesIn,
        ahora: datetime,
    ) -> AutoEnvioReportesPendientesOut:
        pendientes: List[ReporteDiario] = await self._reportes_repo.listar_no_enviados_hasta_fecha(
            fecha=data.fecha
        )

        enviados_ids: List[int] = []

        for reporte in pendientes:
            await self._reportes_repo.marcar_enviado(reporte.id, enviado_en=ahora)
            enviados_ids.append(reporte.id)

            tutor_ids = data.mapa_reporte_tutores.get(reporte.id, [])
            for tutor_id in tutor_ids:
                notif = CrearNotificacionInput(
                    usuario_id=tutor_id,
                    tipo="reporte_diario_auto",
                    payload={
                        "reporte_id": reporte.id,
                        "alumno_id": reporte.alumno_id,
                        "fecha": reporte.fecha.isoformat(),
                    },
                )
                await self._notificaciones_service.crear_notificacion(notif)

        return AutoEnvioReportesPendientesOut(enviados=enviados_ids)
