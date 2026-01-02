# app/kernel/application/exportacion/listar_historial_exportaciones.py

from __future__ import annotations

from pydantic import BaseModel, Field

from app.kernel.domain.exportacion import (
    AbstractExportacionRepository,
    Exportacion,
)


class ListarHistorialExportacionesIn(BaseModel):
    """Input para listar historial."""
    limite: int = Field(default=20, ge=1, le=100)


class ListarHistorialExportacionesOut(BaseModel):
    """Output con historial de exportaciones."""
    exportaciones: list[Exportacion]
    total: int


class ListarHistorialExportacionesCU:
    """
    Caso de uso: Listar historial de exportaciones del usuario actual.
    
    Útil para:
    - Redescargar exportaciones anteriores (si no expiraron)
    - Ver historial de reportes generados
    - Auditoría personal de exportaciones
    
    Ordenado por fecha de solicitud (más reciente primero).
    """
    
    def __init__(
        self,
        exportacion_repo: AbstractExportacionRepository,
        usuario_id: int,
    ) -> None:
        self._repo = exportacion_repo
        self._usuario_id = usuario_id
    
    async def __call__(
        self,
        data: ListarHistorialExportacionesIn,
    ) -> ListarHistorialExportacionesOut:
        """Lista el historial de exportaciones del usuario."""
        
        exportaciones = await self._repo.listar_por_usuario(
            usuario_id=self._usuario_id,
            limite=data.limite,
        )
        
        return ListarHistorialExportacionesOut(
            exportaciones=exportaciones,
            total=len(exportaciones),
        )
