# app/kernel/domain/exportacion/__init__.py

from .exportacion_entidad import (
    Exportacion,
    TipoReporte,
    FormatoArchivo,
    EstadoExportacion,
)

from .plantilla_entidad import PlantillaExportacion

from .errors import (
    ExportacionError,
    ExportacionNoEncontradaError,
    ExportacionNoCompletadaError,
    ExportacionExpiradaError,
    ArchivoNoDisponibleError,
    ErrorProcesamientoExportacion,
    PlantillaNoEncontradaError,
    PlantillaNoAccesibleError,
    PlantillaDuplicadaError,
    FiltrosInvalidosError,
    ColumnasInvalidasError,
)

from .ports import (
    AbstractExportacionRepository,
    AbstractPlantillaExportacionRepository,
    AbstractGeneradorArchivosService,
    AbstractAlmacenamientoService,
)

__all__ = [
    # Entidades
    "Exportacion",
    "TipoReporte",
    "FormatoArchivo",
    "EstadoExportacion",
    "PlantillaExportacion",
    
    # Errores
    "ExportacionError",
    "ExportacionNoEncontradaError",
    "ExportacionNoCompletadaError",
    "ExportacionExpiradaError",
    "ArchivoNoDisponibleError",
    "ErrorProcesamientoExportacion",
    "PlantillaNoEncontradaError",
    "PlantillaNoAccesibleError",
    "PlantillaDuplicadaError",
    "FiltrosInvalidosError",
    "ColumnasInvalidasError",
    
    # Ports
    "AbstractExportacionRepository",
    "AbstractPlantillaExportacionRepository",
    "AbstractGeneradorArchivosService",
    "AbstractAlmacenamientoService",
]
