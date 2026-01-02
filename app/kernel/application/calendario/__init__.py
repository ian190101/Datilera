# app/kernel/application/calendario/__init__.py

from .tipos_eventos import (
    CrearTipoEventoUseCase,
    ObtenerTipoEventoUseCase,
    ListarTiposEventosUseCase,
    ActualizarTipoEventoUseCase,
    ActivarTipoEventoUseCase,
    DesactivarTipoEventoUseCase,
)

from .eventos_calendario import (
    CrearEventoUseCase,
    ObtenerEventoUseCase,
    ListarEventosUseCase,
    ListarEventosPorFechaUseCase,
    ListarEventosPorMesUseCase,
    ActualizarEventoUseCase,
    EliminarEventoUseCase,
    AprobarEventoUseCase,
    RechazarEventoUseCase,
    ProcesarRecordatoriosEventosUseCase,
)

from .planificacion import (
    CrearPlanificacionUseCase,
    ObtenerPlanificacionUseCase,
    ListarPlanificacionesPorFechaUseCase,
    ListarPlanificacionesPorRangoUseCase,
    ListarPlanificacionesProfesoraUseCase,
    ActualizarPlanificacionUseCase,
    EliminarPlanificacionUseCase,
    MarcarCompletadaUseCase,
    ObtenerPlanificacionesPendientesUseCase,
)

__all__ = [
    # Tipos de Eventos
    "CrearTipoEventoUseCase",
    "ObtenerTipoEventoUseCase",
    "ListarTiposEventosUseCase",
    "ActualizarTipoEventoUseCase",
    "ActivarTipoEventoUseCase",
    "DesactivarTipoEventoUseCase",
    
    # Eventos
    "CrearEventoUseCase",
    "ObtenerEventoUseCase",
    "ListarEventosUseCase",
    "ListarEventosPorFechaUseCase",
    "ListarEventosPorMesUseCase",
    "ActualizarEventoUseCase",
    "EliminarEventoUseCase",
    "AprobarEventoUseCase",
    "RechazarEventoUseCase",
    "ProcesarRecordatoriosEventosUseCase",
    
    # Planificación
    "CrearPlanificacionUseCase",
    "ObtenerPlanificacionUseCase",
    "ListarPlanificacionesPorFechaUseCase",
    "ListarPlanificacionesPorRangoUseCase",
    "ListarPlanificacionesProfesoraUseCase",
    "ActualizarPlanificacionUseCase",
    "EliminarPlanificacionUseCase",
    "MarcarCompletadaUseCase",
    "ObtenerPlanificacionesPendientesUseCase",
]
