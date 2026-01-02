# app/kernel/application/exportacion/obtener_estado_exportacion.py

from __future__ import annotations
from datetime import timedelta

from pydantic import BaseModel

from app.kernel.domain.exportacion import (
    AbstractExportacionRepository,
    Exportacion,
    ExportacionNoEncontradaError,
)


class ObtenerEstadoExportacionIn(BaseModel):
    """Input para obtener estado."""
    exportacion_id: int


class ObtenerEstadoExportacionOut(BaseModel):
    """Output con estado de exportación."""
    exportacion: Exportacion
    mensaje: str


class ObtenerEstadoExportacionCU:
    """
    Caso de uso: Consultar el estado de una exportación en proceso.
    
    Estados:
    - PENDIENTE: En cola esperando procesamiento
    - PROCESANDO: Generando archivo
    - COMPLETADO: Listo para descargar
    - ERROR: Falló (ver mensaje de error)
    """
    
    def __init__(
        self,
        exportacion_repo: AbstractExportacionRepository,
    ) -> None:
        self._repo = exportacion_repo
    
    async def __call__(
        self,
        data: ObtenerEstadoExportacionIn,
    ) -> ObtenerEstadoExportacionOut:
        """Obtiene el estado actual de una exportación."""
        
        exportacion = await self._repo.obtener_por_id(data.exportacion_id)
        
        if not exportacion:
            raise ExportacionNoEncontradaError(data.exportacion_id)
        
        # Mensaje según estado
        mensajes = {
            "pendiente": "La exportación está en cola esperando procesamiento",
            "procesando": "Generando archivo de exportación...",
            "completado": f"Exportación completada. Descargue desde /exportacion/{exportacion.id}/descargar",
            "error": f"Error al procesar: {exportacion.error_mensaje or 'Error desconocido'}",
        }
        
        mensaje = mensajes.get(
            exportacion.estado.value,
            "Estado desconocido"
        )
        
        return ObtenerEstadoExportacionOut(
            exportacion=exportacion,
            mensaje=mensaje,
        )
