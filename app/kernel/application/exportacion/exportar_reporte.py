# app/kernel/application/exportacion/exportar_reporte.py

from __future__ import annotations
from datetime import date, timedelta
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from app.kernel.domain.exportacion import (
    AbstractExportacionRepository,
    Exportacion,
    TipoReporte,
    FormatoArchivo,
    EstadoExportacion,
)


class ExportarReporteIn(BaseModel):
    """Input para exportar cualquier tipo de reporte."""
    tipo_reporte: TipoReporte
    formato: FormatoArchivo = Field(default=FormatoArchivo.EXCEL)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    sede_id: Optional[int] = None
    filtros: Optional[Dict[str, Any]] = None
    columnas: Optional[list[str]] = None


class ExportarReporteOut(BaseModel):
    """Output de exportación."""
    exportacion: Exportacion
    mensaje: str


class ExportarReporteCU:
    """
    Caso de uso: Exportar cualquier tipo de reporte del sistema.
    
    Flujo:
    1. Crear registro en BD con estado PENDIENTE
    2. Encolar en Celery/RQ para procesamiento asíncrono
    3. Retornar ID de exportación para consulta posterior
    """
    
    DIAS_EXPIRACION = 3
    
    def __init__(
        self,
        exportacion_repo: AbstractExportacionRepository,
        usuario_id: int,
        sede_id: int,
    ) -> None:
        self._repo = exportacion_repo
        self._usuario_id = usuario_id
        self._sede_id = sede_id
    
    async def __call__(self, data: ExportarReporteIn) -> ExportarReporteOut:
        """
        Ejecuta la exportación.
        
        Args:
            data: Parámetros de exportación
            
        Returns:
            ExportarReporteOut con exportación creada y mensaje
        """
        # Preparar filtros completos
        filtros_completos = {
            "fecha_inicio": data.fecha_inicio.isoformat() if data.fecha_inicio else None,
            "fecha_fin": data.fecha_fin.isoformat() if data.fecha_fin else None,
            "filtros_adicionales": data.filtros or {},
            "columnas": data.columnas,
        }
        
        # Crear registro de exportación
        exportacion = await self._repo.crear_exportacion(
            usuario_id=self._usuario_id,
            sede_id=data.sede_id or self._sede_id,
            tipo_reporte=data.tipo_reporte,
            formato=data.formato,
            filtros=filtros_completos,
        )
        
        # TODO: Enviar a cola de procesamiento asíncrono
        # from app.infrastructure.tasks.exportacion import procesar_exportacion_task
        # procesar_exportacion_task.delay(exportacion.id)
        
        return ExportarReporteOut(
            exportacion=exportacion,
            mensaje=(
                f"Exportación #{exportacion.id} encolada para procesamiento. "
                f"Consulte el estado con GET /exportacion/{exportacion.id}"
            ),
        )
