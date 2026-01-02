# app/kernel/domain/exportacion/errors.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class ExportacionError(Exception):
    """Error base para el dominio de Exportación."""
    code: int
    message: str
    detail: Optional[str] = None
    
    def __str__(self) -> str:
        if self.detail:
            return f"{self.code}: {self.message} ({self.detail})"
        return f"{self.code}: {self.message}"


# ========================================================================
# ERRORES DE EXPORTACIÓN
# ========================================================================

class ExportacionNoEncontradaError(ExportacionError):
    """Error cuando no se encuentra una exportación."""
    exportacion_id: int
    
    def __init__(self, exportacion_id: int) -> None:
        super().__init__(
            code=404,
            message="Exportación no encontrada",
            detail=f"Exportacion id={exportacion_id}",
        )
        self.exportacion_id = exportacion_id


class ExportacionNoCompletadaError(ExportacionError):
    """Error cuando se intenta descargar una exportación no completada."""
    exportacion_id: int
    estado_actual: str
    
    def __init__(self, exportacion_id: int, estado_actual: str) -> None:
        super().__init__(
            code=409,
            message="La exportación no está completada",
            detail=f"Exportacion id={exportacion_id}, estado={estado_actual}",
        )
        self.exportacion_id = exportacion_id
        self.estado_actual = estado_actual


class ExportacionExpiradaError(ExportacionError):
    """Error cuando el archivo de exportación ha expirado."""
    exportacion_id: int
    fecha_expiracion: Optional[date]
    
    def __init__(self, exportacion_id: int, fecha_expiracion: Optional[date]) -> None:
        super().__init__(
            code=410,
            message="El archivo de exportación ha expirado",
            detail=f"Exportacion id={exportacion_id}, expiró el {fecha_expiracion}",
        )
        self.exportacion_id = exportacion_id
        self.fecha_expiracion = fecha_expiracion


class ArchivoNoDisponibleError(ExportacionError):
    """Error cuando el archivo físico no está disponible."""
    exportacion_id: int
    razon: str
    
    def __init__(self, exportacion_id: int, razon: str) -> None:
        super().__init__(
            code=404,
            message="Archivo no disponible",
            detail=f"Exportacion id={exportacion_id}: {razon}",
        )
        self.exportacion_id = exportacion_id
        self.razon = razon


class ErrorProcesamientoExportacion(ExportacionError):
    """Error durante el procesamiento de una exportación."""
    exportacion_id: int
    error_tecnico: str
    
    def __init__(self, exportacion_id: int, error_tecnico: str) -> None:
        super().__init__(
            code=500,
            message="Error al procesar exportación",
            detail=f"Exportacion id={exportacion_id}: {error_tecnico}",
        )
        self.exportacion_id = exportacion_id
        self.error_tecnico = error_tecnico


# ========================================================================
# ERRORES DE PLANTILLAS
# ========================================================================

class PlantillaNoEncontradaError(ExportacionError):
    """Error cuando no se encuentra una plantilla."""
    plantilla_id: int
    
    def __init__(self, plantilla_id: int) -> None:
        super().__init__(
            code=404,
            message="Plantilla no encontrada",
            detail=f"PlantillaExportacion id={plantilla_id}",
        )
        self.plantilla_id = plantilla_id


class PlantillaNoAccesibleError(ExportacionError):
    """Error cuando el usuario no puede acceder a una plantilla."""
    plantilla_id: int
    razon: str
    
    def __init__(self, plantilla_id: int, razon: str) -> None:
        super().__init__(
            code=403,
            message="No tiene permisos para usar esta plantilla",
            detail=f"PlantillaExportacion id={plantilla_id}: {razon}",
        )
        self.plantilla_id = plantilla_id
        self.razon = razon


class PlantillaDuplicadaError(ExportacionError):
    """Error cuando se intenta crear una plantilla con nombre duplicado."""
    nombre: str
    
    def __init__(self, nombre: str) -> None:
        super().__init__(
            code=409,
            message="Ya existe una plantilla con ese nombre",
            detail=f"Nombre: {nombre}",
        )
        self.nombre = nombre


# ========================================================================
# ERRORES DE VALIDACIÓN
# ========================================================================

class FiltrosInvalidosError(ExportacionError):
    """Error cuando los filtros de exportación son inválidos."""
    razon: str
    
    def __init__(self, razon: str) -> None:
        super().__init__(
            code=400,
            message="Filtros de exportación inválidos",
            detail=razon,
        )
        self.razon = razon


class ColumnasInvalidasError(ExportacionError):
    """Error cuando las columnas seleccionadas son inválidas."""
    columnas_invalidas: list
    
    def __init__(self, columnas_invalidas: list) -> None:
        super().__init__(
            code=400,
            message="Columnas inválidas para este tipo de reporte",
            detail=f"Columnas no reconocidas: {', '.join(columnas_invalidas)}",
        )
        self.columnas_invalidas = columnas_invalidas
