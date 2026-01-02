# app/kernel/application/exportacion/eliminar_exportacion.py

from __future__ import annotations
from pathlib import Path

from pydantic import BaseModel

from app.kernel.domain.exportacion import (
    AbstractExportacionRepository,
    ExportacionNoEncontradaError,
)


class EliminarExportacionIn(BaseModel):
    """Input para eliminar exportación."""
    exportacion_id: int


class EliminarExportacionOut(BaseModel):
    """Output de eliminación."""
    mensaje: str


class EliminarExportacionCU:
    """
    Caso de uso: Eliminar manualmente una exportación.
    
    Útil para:
    - Liberar espacio en disco antes de la expiración
    - Eliminar exportaciones con datos sensibles
    - Limpiar historial personal
    
    Elimina:
    1. El archivo físico del disco (si existe)
    2. El registro de la base de datos
    """
    
    def __init__(
        self,
        exportacion_repo: AbstractExportacionRepository,
    ) -> None:
        self._repo = exportacion_repo
    
    async def __call__(
        self,
        data: EliminarExportacionIn,
    ) -> EliminarExportacionOut:
        """Elimina una exportación del sistema."""
        
        # Obtener exportación
        exportacion = await self._repo.obtener_por_id(data.exportacion_id)
        
        if not exportacion:
            raise ExportacionNoEncontradaError(data.exportacion_id)
        
        # Eliminar archivo físico si existe
        if exportacion.ruta_archivo:
            ruta = Path(exportacion.ruta_archivo)
            if ruta.exists():
                try:
                    ruta.unlink()
                except Exception as e:
                    # Log error pero continuar con eliminación de registro
                    print(f"Error al eliminar archivo: {e}")
        
        # Eliminar registro de BD
        await self._repo.eliminar_exportacion(data.exportacion_id)
        
        return EliminarExportacionOut(
            mensaje=f"Exportación #{data.exportacion_id} eliminada correctamente"
        )
