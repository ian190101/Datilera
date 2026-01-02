# app/kernel/domain/calendario/entities/__init__.py

from .tipo_evento_entidad import TipoEvento
from .evento_calendario_entidad import EventoCalendario
from .planificacion_actividad_entidad import PlanificacionActividad
from .ports import TipoEventoRepositoryPort, EventoCalendarioRepositoryPort, PlanificacionActividadRepositoryPort
from .errors import (
    # Tipos de Eventos
    TipoEventoNoEncontradoError,
    TipoEventoDuplicadoError,
    TipoEventoInactivoError,
    TipoEventoEnUsoError,
    
    # Eventos
    EventoNoEncontradoError,
    EventoDuplicadoError,
    EventoFechaInvalidaError,
    EventoHoraInvalidaError,
    EventoFechaFuturaRequeridaError,
    EventoPendienteAprobacionError,
    EventoYaAprobadoError,
    EventoRecordatorioYaEnviadoError,
    EventoSinPermisosError,
    
    # Planificaciones
    PlanificacionNoEncontradaError,
    PlanificacionDuplicadaError,
    PlanificacionHorarioConflictoError,
    PlanificacionFechaInvalidaError,
    PlanificacionHoraInvalidaError,
    PlanificacionYaCompletadaError,
    PlanificacionNoCompletadaError,
    PlanificacionFueraDePeriodoError,
    PlanificacionSinProfesoraError,
    PlanificacionSinPermisosError,
    
    # Validación General
    CalendarioFechaInvalidaError,
    CalendarioHorarioInvalidoError,
    CalendarioDatosInvalidosError,
    CalendarioCampoRequeridoError,
    CalendarioColorInvalidoError,
    CalendarioSedeNoCoincideError,
    
    # Permisos
    CalendarioPermisosDenegadosError,
    CalendarioNoEsProfesoraError,
    CalendarioNoEsDirectoraError,
    
    # Relaciones
    CalendarioParaleloNoEncontradoError,
    CalendarioProfesoraNoEncontradaError,
    CalendarioSedeNoEncontradaError,
    CalendarioRelacionInvalidaError,
)

__all__ = [
    "TipoEvento",
    "EventoCalendario",
    "PlanificacionActividad",
    "TipoEventoRepositoryPort",
    "EventoCalendarioRepositoryPort",
    "PlanificacionActividadRepositoryPort",
    # Errors - Tipos de Eventos
    "TipoEventoNoEncontradoError",
    "TipoEventoDuplicadoError",
    "TipoEventoInactivoError",
    "TipoEventoEnUsoError",
    
    # Errors - Eventos
    "EventoNoEncontradoError",
    "EventoDuplicadoError",
    "EventoFechaInvalidaError",
    "EventoHoraInvalidaError",
    "EventoFechaFuturaRequeridaError",
    "EventoPendienteAprobacionError",
    "EventoYaAprobadoError",
    "EventoRecordatorioYaEnviadoError",
    "EventoSinPermisosError",
    
    # Errors - Planificaciones
    "PlanificacionNoEncontradaError",
    "PlanificacionDuplicadaError",
    "PlanificacionHorarioConflictoError",
    "PlanificacionFechaInvalidaError",
    "PlanificacionHoraInvalidaError",
    "PlanificacionYaCompletadaError",
    "PlanificacionNoCompletadaError",
    "PlanificacionFueraDePeriodoError",
    "PlanificacionSinProfesoraError",
    "PlanificacionSinPermisosError",
    
    # Errors - Validación
    "CalendarioFechaInvalidaError",
    "CalendarioHorarioInvalidoError",
    "CalendarioDatosInvalidosError",
    "CalendarioCampoRequeridoError",
    "CalendarioColorInvalidoError",
    "CalendarioSedeNoCoincideError",
    
    # Errors - Permisos
    "CalendarioPermisosDenegadosError",
    "CalendarioNoEsProfesoraError",
    "CalendarioNoEsDirectoraError",
    
    # Errors - Relaciones
    "CalendarioParaleloNoEncontradoError",
    "CalendarioProfesoraNoEncontradaError",
    "CalendarioSedeNoEncontradaError",
    "CalendarioRelacionInvalidaError",
]
