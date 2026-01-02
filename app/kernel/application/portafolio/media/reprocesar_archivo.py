# app/kernel/application/portafolio/media/reprocesar_archivo.py

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ArchivoMediaPortafolio,
    AbstractActividadMediaRepository,
    MediaNoEncontradaError,
    MediaProcesamientoError,
    MediaIntentosExcedidosError,
)
from app.kernel.domain.portafolio.actividad_media_entidad import (
    EstadoProcesamientoWatermark
)


class ReprocesarArchivoIn(BaseModel):
    """Input para reprocesar un archivo con marca de agua."""
    media_id: int = Field(gt=0, description="ID del archivo a reprocesar")


class ReprocesarArchivoOut(BaseModel):
    """Output con el archivo actualizado."""
    media: ArchivoMediaPortafolio
    mensaje: str
    nueva_cola_id: str


class ReprocesarArchivoCU:
    """
    Caso de uso: Forzar el reprocesamiento de un archivo con marca de agua.
    
    Permite reintentar el procesamiento de archivos que:
    - Fallaron con error
    - Están pendientes pero no se procesaron
    
    No permite reprocesar archivos que:
    - Ya están completados correctamente
    - Excedieron el máximo de intentos
    - Están marcados como "no aplica"
    """
    
    MAX_INTENTOS = 3
    
    def __init__(
        self,
        media_repo: AbstractActividadMediaRepository,
    ) -> None:
        self._media_repo = media_repo
    
    async def __call__(
        self,
        data: ReprocesarArchivoIn,
    ) -> ReprocesarArchivoOut:
        """
        Ejecuta el caso de uso.
        
        Args:
            data: Datos de entrada con media_id
            
        Returns:
            ReprocesarArchivoOut con el archivo actualizado
            
        Raises:
            MediaNoEncontradaError: Si el archivo no existe
            MediaNoReprocesableError: Si el archivo no puede reprocesarse
            MediaIntentosExcedidosError: Si excedió intentos máximos
        """
        # Obtener archivo
        media = await self._media_repo.obtener_por_id(data.media_id)
        
        if media is None:
            raise MediaNoEncontradaError(media_id=data.media_id)
        
        # Validar que puede reprocesarse
        if not media.puede_reprocesar:
            # Determinar razón específica
            if media.estado_procesamiento == EstadoProcesamientoWatermark.COMPLETADO:
                raise MediaProcesamientoError(
                    media_id=data.media_id,
                    razon="El archivo ya está procesado correctamente"
                )
            elif media.intentos_procesamiento >= self.MAX_INTENTOS:
                raise MediaIntentosExcedidosError(
                    media_id=data.media_id,
                    intentos=media.intentos_procesamiento,
                    max_intentos=self.MAX_INTENTOS
                )
            else:
                raise MediaProcesamientoError(
                    media_id=data.media_id,
                    razon=f"Estado: {media.estado_procesamiento.value}"
                )
        
        # Generar nuevo ID de cola
        nueva_cola_id = f"retry_{data.media_id}_{int(datetime.now().timestamp())}"
        
        # Actualizar estado para reprocesamiento
        await self._media_repo.actualizar_procesamiento(
            media_id=data.media_id,
            estado_procesamiento=EstadoProcesamientoWatermark.PENDIENTE,
            cola_id=nueva_cola_id,
            error=None,  # Limpiar error anterior
        )
        
        # Incrementar contador de intentos
        await self._media_repo.incrementar_intentos(data.media_id)
        
        # TODO: Aquí enviarías a la cola Celery/RQ
        # from app.infrastructure.tasks.watermark import aplicar_marca_agua_task
        # aplicar_marca_agua_task.delay(data.media_id)
        
        # Recargar archivo actualizado
        media_actualizada = await self._media_repo.obtener_por_id(data.media_id)
        
        if media_actualizada is None:
            raise MediaNoEncontradaError(media_id=data.media_id)
        
        return ReprocesarArchivoOut(
            media=media_actualizada,
            mensaje=f"Archivo enviado a cola de reprocesamiento (intento {media_actualizada.intentos_procesamiento}/{self.MAX_INTENTOS})",
            nueva_cola_id=nueva_cola_id
        )
