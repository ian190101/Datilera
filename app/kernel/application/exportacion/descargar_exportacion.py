# app/kernel/application/exportacion/descargar_exportacion.py

from __future__ import annotations
from pathlib import Path

from pydantic import BaseModel

from app.kernel.domain.exportacion import (
    AbstractExportacionRepository,
    Exportacion,
    ExportacionNoEncontradaError,
    ArchivoNoDisponibleError,
)


class DescargarExportacionIn(BaseModel):
    """Input para descargar exportación."""
    exportacion_id: int


class DescargarExportacionOut(BaseModel):
    """Output con información para descarga."""
    ruta_archivo: str
    nombre_archivo: str
    tipo_contenido: str


class DescargarExportacionCU:
    """
    Caso de uso: Descargar archivo de exportación completado.
    
    Validaciones:
    - La exportación debe estar en estado COMPLETADO
    - El archivo no debe haber expirado
    - El archivo debe existir físicamente en disco
    
    Incrementa el contador de descargas.
    """
    
    TIPOS_MIME = {
        "pdf": "application/pdf",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
    }
    
    def __init__(
        self,
        exportacion_repo: AbstractExportacionRepository,
    ) -> None:
        self._repo = exportacion_repo
    
    async def __call__(
        self,
        data: DescargarExportacionIn,
    ) -> DescargarExportacionOut:
        """Valida y retorna información para descarga."""
        
        # Obtener exportación
        exportacion = await self._repo.obtener_por_id(data.exportacion_id)
        
        if not exportacion:
            raise ExportacionNoEncontradaError(data.exportacion_id)
        
        # Validar que puede descargarse (usa método de la entidad)
        exportacion.validar_descarga()
        
        # Verificar que el archivo existe físicamente
        ruta = Path(exportacion.ruta_archivo)
        if not ruta.exists():
            raise ArchivoNoDisponibleError(
                data.exportacion_id,
                "El archivo ya no existe en el servidor"
            )
        
        # Incrementar contador de descargas
        await self._repo.incrementar_descargas(data.exportacion_id)
        
        # Determinar tipo MIME
        tipo_contenido = self.TIPOS_MIME.get(
            exportacion.formato.value,
            "application/octet-stream"
        )
        
        return DescargarExportacionOut(
            ruta_archivo=str(ruta),
            nombre_archivo=exportacion.nombre_archivo,
            tipo_contenido=tipo_contenido,
        )
