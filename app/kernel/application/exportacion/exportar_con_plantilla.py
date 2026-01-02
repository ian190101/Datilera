# app/kernel/application/exportacion/exportar_con_plantilla.py

from __future__ import annotations
from typing import Optional, Dict, Any

from pydantic import BaseModel

from app.kernel.domain.exportacion import (
    AbstractExportacionRepository,
    AbstractPlantillaExportacionRepository,
    Exportacion,
    PlantillaNoEncontradaError,
)


class ExportarConPlantillaIn(BaseModel):
    """Input para exportar usando plantilla."""
    plantilla_id: int
    filtros_override: Optional[Dict[str, Any]] = None


class ExportarConPlantillaOut(BaseModel):
    """Output de exportación con plantilla."""
    exportacion: Exportacion
    plantilla_usada: str
    mensaje: str


class ExportarConPlantillaCU:
    """
    Caso de uso: Exportar usando una plantilla predefinida.
    
    Ventajas:
    - No necesita especificar columnas ni tipo de reporte
    - Usa configuración guardada de la plantilla
    - Permite sobrescribir filtros específicos si es necesario
    
    Ejemplo:
    - Plantilla "Reporte Mensual Pagos" ya tiene columnas y formato
    - Usuario solo especifica fecha_inicio y fecha_fin como override
    """
    
    def __init__(
        self,
        exportacion_repo: AbstractExportacionRepository,
        plantilla_repo: AbstractPlantillaExportacionRepository,
        usuario_id: int,
        sede_id: int,
    ) -> None:
        self._exportacion_repo = exportacion_repo
        self._plantilla_repo = plantilla_repo
        self._usuario_id = usuario_id
        self._sede_id = sede_id
    
    async def __call__(
        self,
        data: ExportarConPlantillaIn,
    ) -> ExportarConPlantillaOut:
        """Exporta usando configuración de plantilla."""
        
        # Obtener plantilla
        plantilla = await self._plantilla_repo.obtener_por_id(data.plantilla_id)
        
        if not plantilla:
            raise PlantillaNoEncontradaError(data.plantilla_id)
        
        # Validar que el usuario puede usarla (usa método de entidad)
        plantilla.validar_uso(self._usuario_id)
        
        # Combinar filtros de plantilla con override del usuario
        filtros_finales = plantilla.filtros_default or {}
        if data.filtros_override:
            filtros_finales.update(data.filtros_override)
        
        # Agregar columnas de la plantilla
        filtros_finales["columnas"] = plantilla.columnas_incluidas
        
        # Crear exportación usando configuración de plantilla
        exportacion = await self._exportacion_repo.crear_exportacion(
            usuario_id=self._usuario_id,
            sede_id=self._sede_id,
            tipo_reporte=plantilla.tipo_reporte,
            formato=plantilla.formato_default,
            filtros=filtros_finales,
            plantilla_id=plantilla.id,
        )
        
        # TODO: Enviar a cola
        # from app.infrastructure.tasks.exportacion import procesar_exportacion_task
        # procesar_exportacion_task.delay(exportacion.id)
        
        return ExportarConPlantillaOut(
            exportacion=exportacion,
            plantilla_usada=plantilla.nombre,
            mensaje=(
                f"Exportación #{exportacion.id} encolada usando plantilla '{plantilla.nombre}'. "
                f"Consulte el estado con GET /exportacion/{exportacion.id}"
            ),
        )
