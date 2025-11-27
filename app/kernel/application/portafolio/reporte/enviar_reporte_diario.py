from __future__ import annotations

from datetime import datetime, time
from typing import List

from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ReporteDiario,
    AbstractReportesDiariosRepository,
    ReporteNoEncontradoError,
)

# 1. CORRECCIÓN: Usamos el nombre real de la interfaz (Abstract...)
from app.kernel.domain.notificaciones.notificaciones import (
    CrearNotificacionInput,
    AbstractNotificacionesService, 
)

LIMITE_ENVIO_REPORTE = time(20, 0)  # 20:00


class EnviarReporteDiarioIn(BaseModel):
    reporte_id: int = Field(gt=0)
    tutor_ids: List[int] = Field(default_factory=list)


class EnviarReporteDiarioOut(BaseModel):
    reporte: ReporteDiario


class EnviarReporteDiarioCU:
    def __init__(
        self,
        reportes_repo: AbstractReportesDiariosRepository,
        # 2. CORRECCIÓN: Type Hint actualizado
        notificaciones_service: AbstractNotificacionesService,
    ) -> None:
        self._reportes_repo = reportes_repo
        self._notificaciones_service = notificaciones_service

    async def execute( # Sugerencia: Usar 'execute' es más explícito que __call__, pero __call__ funciona
        self,
        data: EnviarReporteDiarioIn,
        # Hacer 'ahora' opcional facilita el testeo y uso en el router
        ahora: datetime | None = None, 
    ) -> EnviarReporteDiarioOut:
        
        if ahora is None:
            ahora = datetime.now()

        reporte = await self._reportes_repo.obtener_por_id(data.reporte_id)
        if reporte is None:
            raise ReporteNoEncontradoError(reporte_id=data.reporte_id)

        # Lógica de negocio: Solo enviar si es antes de las 20:00 y no se ha enviado antes
        # (Ojo: Podrías querer lanzar error si ya fue enviado, pero aquí lo ignoramos silenciosamente)
        if ahora.time() <= LIMITE_ENVIO_REPORTE and not reporte.enviado:
            await self._reportes_repo.marcar_enviado(
                reporte_id=reporte.id,
                enviado_en=ahora,
            )
            
            for tutor_id in data.tutor_ids:
                # 3. CORRECCIÓN: Alinear campos con CrearNotificacionInput definido en Dominio
                # Faltaban 'titulo' y 'mensaje'. Cambiamos 'payload' por 'data'.
                notif = CrearNotificacionInput(
                    usuario_id=tutor_id,
                    titulo="Nuevo Reporte Diario",
                    mensaje=f"Se ha publicado el reporte del día {reporte.fecha}",
                    tipo="reporte_diario",
                    data={ 
                        "reporte_id": reporte.id,
                        "alumno_id": reporte.alumno_id,
                        "fecha": reporte.fecha.isoformat(),
                    },
                )
                
                # 4. CORRECCIÓN: Usar el método definido en la interfaz (enviar_notificacion)
                # Antes llamabas a 'crear_notificacion'
                await self._notificaciones_service.enviar_notificacion(notif)

        actualizado = await self._reportes_repo.obtener_por_id(data.reporte_id)
        # Usamos un check seguro
        if actualizado is None:
             raise ReporteNoEncontradoError(reporte_id=data.reporte_id)
             
        return EnviarReporteDiarioOut(reporte=actualizado)