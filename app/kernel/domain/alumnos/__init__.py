# app/domain/errors/alumnos/__init__.py

from .errors import (
    # Alumnos
    AlumnoNoEncontradoError,
    AlumnoDuplicadoError,
    AlumnoInactivoError,
    AlumnoMenorEdadError,
    # Tutores
    TutorNoEncontradoError,
    TutorDuplicadoError,
    TutorSinAlumnosError,
    # Relaciones
    RelacionAlumnoTutorNoEncontradaError,
    RelacionAlumnoTutorDuplicadaError,
    TutorPrincipalDuplicadoError,
    # Hermanos
    HermanoNoEncontradoError,
    # Autorizaciones
    AutorizacionRetiroNoEncontradaError,
    AutorizacionRetiroDuplicadaError,
    AutorizacionRetiroInactivaError,
    # Asistencia
    AsistenciaNoEncontradaError,
    AsistenciaDuplicadaError,
    AsistenciaFechaFuturaError,
    # Permisos
    PermisoNoEncontradoError,
    PermisoYaAprobadoError,
    PermisoFechasInvalidasError,
    # Consentimientos
    ConsentimientoNoEncontradoError,
    # Paralelos
    AsignacionParaleloNoEncontradaError,
    AsignacionParaleloDuplicadaError,
    # Generales
    DatosInvalidosError,
    CampoRequeridoError,
)

__all__ = [
    # Alumnos
    "AlumnoNoEncontradoError",
    "AlumnoDuplicadoError",
    "AlumnoInactivoError",
    "AlumnoMenorEdadError",
    # Tutores
    "TutorNoEncontradoError",
    "TutorDuplicadoError",
    "TutorSinAlumnosError",
    # Relaciones
    "RelacionAlumnoTutorNoEncontradaError",
    "RelacionAlumnoTutorDuplicadaError",
    "TutorPrincipalDuplicadoError",
    # Hermanos
    "HermanoNoEncontradoError",
    # Autorizaciones
    "AutorizacionRetiroNoEncontradaError",
    "AutorizacionRetiroDuplicadaError",
    "AutorizacionRetiroInactivaError",
    # Asistencia
    "AsistenciaNoEncontradaError",
    "AsistenciaDuplicadaError",
    "AsistenciaFechaFuturaError",
    # Permisos
    "PermisoNoEncontradoError",
    "PermisoYaAprobadoError",
    "PermisoFechasInvalidasError",
    # Consentimientos
    "ConsentimientoNoEncontradoError",
    # Paralelos
    "AsignacionParaleloNoEncontradaError",
    "AsignacionParaleloDuplicadaError",
    # Generales
    "DatosInvalidosError",
    "CampoRequeridoError",
]
