# app/kernel/application/portafolio/media/listar_archivos_cola.py

from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field

from app.kernel.domain.portafolio import (
    ArchivoMediaPortafolio,
    AbstractActividadMediaRepository,
)
from app.kernel.domain.portafolio.actividad_media_entidad import (
    EstadoProcesamientoWatermark
)


class ListarArchivosColaIn(BaseModel):
    """Input para listar archivos en cola de procesamiento."""
    tipo: str = Field(
        default="pendientes",
        description="Tipo de archivos a listar: 'pendientes' o 'errores'"
    )
    limite: int = Field(default=50, ge=1, le=200, description="Límite de resultados")


class ListarArchivosColaOut(BaseModel):
    """Output con lista de archivos."""
    archivos: List[ArchivoMediaPortafolio]
    total: int


class ListarArchivosColaCU:
    """
    Caso de uso: Listar archivos en cola de procesamiento.
    
    Permite listar:
    - Archivos pendientes o en procesamiento
    - Archivos con error de procesamiento
    
    Útil para:
    - Dashboard de monitoreo
    - Detectar archivos estancados
    - Ver errores de procesamiento
    """
    
    def __init__(
        self,
        media_repo: AbstractActividadMediaRepository,
    ) -> None:
        self._media_repo = media_repo
    
    async def __call__(
        self,
        data: ListarArchivosColaIn,
    ) -> ListarArchivosColaOut:
        """
        Ejecuta el caso de uso.
        
        Args:
            data: Datos de entrada con tipo y límite
            
        Returns:
            ListarArchivosColaOut con lista de archivos
        """
        if data.tipo == "pendientes":
            # Lista archivos pendientes o en procesamiento
            estados = [
                EstadoProcesamientoWatermark.PENDIENTE,
                EstadoProcesamientoWatermark.PROCESANDO,
            ]
        elif data.tipo == "errores":
            # Lista solo archivos con error
            estados = [EstadoProcesamientoWatermark.ERROR]
        else:
            # Default: pendientes
            estados = [
                EstadoProcesamientoWatermark.PENDIENTE,
                EstadoProcesamientoWatermark.PROCESANDO,
            ]
        
        archivos = await self._media_repo.listar_por_estado_procesamiento(
            estados=estados,
            limite=data.limite,
        )
        
        return ListarArchivosColaOut(
            archivos=archivos,
            total=len(archivos)
        )
