# app/kernel/application/portafolio/media/obtener_estado_procesamiento.py

from __future__ import annotations
from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ArchivoMediaPortafolio,
    AbstractActividadMediaRepository,
    MediaNoEncontradaError,
)


class ObtenerEstadoProcesamientoIn(BaseModel):
    """Input para obtener estado de procesamiento de marca de agua."""
    media_id: int = Field(gt=0, description="ID del archivo multimedia")


class ObtenerEstadoProcesamientoOut(BaseModel):
    """Output con el estado de procesamiento."""
    media: ArchivoMediaPortafolio


class ObtenerEstadoProcesamientoCU:
    """
    Caso de uso: Obtener el estado de procesamiento de marca de agua de un archivo.
    
    Permite consultar:
    - Estado actual (pendiente, procesando, completado, error)
    - Número de intentos de procesamiento
    - Mensaje de error si falló
    - ID de la cola de procesamiento
    - Fecha de procesamiento completado
    """
    
    def __init__(
        self,
        media_repo: AbstractActividadMediaRepository,
    ) -> None:
        self._media_repo = media_repo
    
    async def __call__(
        self,
        data: ObtenerEstadoProcesamientoIn,
    ) -> ObtenerEstadoProcesamientoOut:
        """
        Ejecuta el caso de uso.
        
        Args:
            data: Datos de entrada con media_id
            
        Returns:
            ObtenerEstadoProcesamientoOut con la entidad completa
            
        Raises:
            MediaNoEncontradaError: Si el archivo no existe
        """
        media = await self._media_repo.obtener_por_id(data.media_id)
        
        if media is None:
            raise MediaNoEncontradaError(media_id=data.media_id)
        
        return ObtenerEstadoProcesamientoOut(media=media)
