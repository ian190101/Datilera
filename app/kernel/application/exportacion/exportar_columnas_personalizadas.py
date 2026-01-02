# app/kernel/application/exportacion/exportar_columnas_personalizadas.py

from __future__ import annotations
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from app.kernel.domain.exportacion import (
    AbstractExportacionRepository,
    AbstractPlantillaExportacionRepository,
    Exportacion,
    TipoReporte,
    FormatoArchivo,
    PlantillaDuplicadaError,
)


class ExportarColumnasPersonalizadasIn(BaseModel):
    """Input para exportación con columnas personalizadas."""
    tipo_reporte: TipoReporte
    formato: FormatoArchivo
    columnas_seleccionadas: list[str] = Field(min_length=1)
    filtros: Optional[Dict[str, Any]] = None
    guardar_como_plantilla: bool = Field(default=False)
    nombre_plantilla: Optional[str] = None
    descripcion_plantilla: Optional[str] = None


class ExportarColumnasPersonalizadasOut(BaseModel):
    """Output de exportación con columnas personalizadas."""
    exportacion: Exportacion
    plantilla_creada_id: Optional[int] = None
    mensaje: str


class ExportarColumnasPersonalizadasCU:
    """
    Caso de uso: Exportar con columnas seleccionadas por el usuario.
    
    Opcionalmente guarda la configuración como plantilla reutilizable.
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
        data: ExportarColumnasPersonalizadasIn,
    ) -> ExportarColumnasPersonalizadasOut:
        """Ejecuta la exportación con columnas personalizadas."""
        
        # TODO: Validar que las columnas sean válidas para el tipo de reporte
        # self._validar_columnas(data.tipo_reporte, data.columnas_seleccionadas)
        
        # Crear exportación
        filtros_completos = {
            "filtros_adicionales": data.filtros or {},
            "columnas": data.columnas_seleccionadas,
        }
        
        exportacion = await self._exportacion_repo.crear_exportacion(
            usuario_id=self._usuario_id,
            sede_id=self._sede_id,
            tipo_reporte=data.tipo_reporte,
            formato=data.formato,
            filtros=filtros_completos,
        )
        
        # Guardar como plantilla si se solicita
        plantilla_id = None
        if data.guardar_como_plantilla and data.nombre_plantilla:
            # Verificar que no exista plantilla con ese nombre
            plantilla_existente = await self._plantilla_repo.obtener_por_nombre(
                data.nombre_plantilla
            )
            
            if plantilla_existente:
                raise PlantillaDuplicadaError(data.nombre_plantilla)
            
            plantilla = await self._plantilla_repo.crear_plantilla(
                nombre=data.nombre_plantilla,
                descripcion=data.descripcion_plantilla,
                tipo_reporte=data.tipo_reporte,
                formato_default=data.formato,
                columnas_incluidas=data.columnas_seleccionadas,
                filtros_default=data.filtros,
                creado_por=self._usuario_id,
                es_publica=False,  # Por defecto privada
            )
            plantilla_id = plantilla.id
        
        mensaje = f"Exportación #{exportacion.id} encolada."
        if plantilla_id:
            mensaje += f" Plantilla guardada con ID {plantilla_id}."
        
        return ExportarColumnasPersonalizadasOut(
            exportacion=exportacion,
            plantilla_creada_id=plantilla_id,
            mensaje=mensaje,
        )
