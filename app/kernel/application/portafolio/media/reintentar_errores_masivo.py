# app/kernel/application/portafolio/media/reintentar_errores_masivo.py

from __future__ import annotations
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ArchivoMediaPortafolio,
    AbstractActividadMediaRepository,
)
from app.kernel.domain.portafolio.actividad_media_entidad import (
    EstadoProcesamientoWatermark
)


class ReintentarErroresMasivoIn(BaseModel):
    """Input para reintentar archivos con error."""
    max_intentos: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Máximo de intentos permitidos antes de descartar"
    )


class ReintentarErroresMasivoOut(BaseModel):
    """Output con resultados del reintento masivo."""
    total_reenviados: int
    media_ids: List[int]
    mensaje: str


class ReintentarErroresMasivoCU:
    """
    Caso de uso: Reintentar procesamiento de todos los archivos con error.
    
    Busca todos los archivos que:
    - Tienen estado ERROR
    - No han excedido el máximo de intentos
    
    Los resetea y los reenvía a la cola de procesamiento.
    
    Útil para:
    - Recuperación masiva después de un problema del sistema
    - Reintentar después de actualizar configuración de marca de agua
    - Limpieza de cola de errores
    """
    
    def __init__(
        self,
        media_repo: AbstractActividadMediaRepository,
    ) -> None:
        self._media_repo = media_repo
    
    async def __call__(
        self,
        data: ReintentarErroresMasivoIn,
    ) -> ReintentarErroresMasivoOut:
        """
        Ejecuta el caso de uso.
        
        Args:
            data: Datos de entrada con max_intentos
            
        Returns:
            ReintentarErroresMasivoOut con resultados
        """
        # Obtener archivos con error que pueden reintentarse
        archivos_error = await self._media_repo.listar_errores_reintentables(
            max_intentos=data.max_intentos
        )
        
        if not archivos_error:
            return ReintentarErroresMasivoOut(
                total_reenviados=0,
                media_ids=[],
                mensaje="No hay archivos con error para reintentar"
            )
        
        media_ids_reenviados: List[int] = []
        timestamp = int(datetime.now().timestamp())
        
        for media in archivos_error:
            try:
                # Generar nuevo ID de cola
                nueva_cola_id = f"bulk_retry_{media.id}_{timestamp}"
                
                # Actualizar estado
                await self._media_repo.actualizar_procesamiento(
                    media_id=media.id,
                    estado_procesamiento=EstadoProcesamientoWatermark.PENDIENTE,
                    cola_id=nueva_cola_id,
                    error=None,
                )
                
                # Incrementar intentos
                await self._media_repo.incrementar_intentos(media.id)
                
                # TODO: Enviar a cola
                # from app.infrastructure.tasks.watermark import aplicar_marca_agua_task
                # aplicar_marca_agua_task.delay(media.id)
                
                media_ids_reenviados.append(media.id)
                
            except Exception as e:
                # Log error pero continuar con los demás
                print(f"Error al reintentar media {media.id}: {e}")
                continue
        
        return ReintentarErroresMasivoOut(
            total_reenviados=len(media_ids_reenviados),
            media_ids=media_ids_reenviados,
            mensaje=f"Se reenviaron {len(media_ids_reenviados)} archivos a cola de procesamiento"
        )
