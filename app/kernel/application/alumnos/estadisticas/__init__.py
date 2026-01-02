# app/kernel/application/asistencia/estadisticas/__init__.py

from .obtener_estadisticas_paralelo import ObtenerEstadisticasParaleloUseCase
from .obtener_estadisticas_sede import ObtenerEstadisticasSedeUseCase
from .obtener_reporte_retrasos import ObtenerReporteRetrasosUseCase
from .obtener_reporte_faltas import ObtenerReporteFaltasUseCase

__all__ = [
    "ObtenerEstadisticasParaleloUseCase",
    "ObtenerEstadisticasSedeUseCase",
    "ObtenerReporteRetrasosUseCase",
    "ObtenerReporteFaltasUseCase",
]
