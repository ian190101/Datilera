# app/kernel/dominio/portafolio/__init__.py
from __future__ import annotations

# 1. Entidades
from .actividad_entidad import ActividadPortafolio
from .actividad_media_entidad import ArchivoMediaPortafolio, TipoMedia, PoliticaExpiracionMedia, EstadoMedia
from .reporte_diario_entidad import ReporteDiario
from .reporte_lectura_tutor_entidad import LecturaTutor

# 2. Puertos / Interfaces (LO QUE FALTABA)
# Asegúrate de que tu archivo se llame 'puertos.py'. Si se llama 'ports.py', cambia la importación.
from .ports import (
    AbstractReportesDiariosRepository,
    AbstractReporteLecturasTutoresRepository,
    AbstractActividadesRepository,
    AbstractActividadMediaRepository,
    AbstractStorageService,
)

# 3. Errores (LO QUE FALTABA)
# Asegúrate de que tu archivo se llame 'errores.py'. Si se llama 'errors.py', cambia la importación.
from .errors import (
    PortafolioError,
    ReporteNoEncontradoError,
    ActividadNoEncontradaError,
    MediaNoEncontradaError,
    MediaNoDisponibleError,
    MediaExpiradaError,
    MediaProcesamientoError,
    MediaIntentosExcedidosError,
)

__all__ = [
    # Entidades
    "ActividadPortafolio",
    "ArchivoMediaPortafolio", 
    "TipoMedia",
    "PoliticaExpiracionMedia",
    "ReporteDiario",
    "LecturaTutor",
    "EstadoMedia",

    # Puertos
    "AbstractReportesDiariosRepository",
    "AbstractReporteLecturasTutoresRepository",
    "AbstractActividadesRepository",
    "AbstractActividadMediaRepository",
    "AbstractStorageService",

    # Errores
    "PortafolioError",
    "ReporteNoEncontradoError",
    "ActividadNoEncontradaError",
    "MediaNoEncontradaError",
    "MediaNoDisponibleError",
    "MediaExpiradaError",
    "MediaProcesamientoError",
    "MediaIntentosExcedidosError",
]