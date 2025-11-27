# app/infrastructure/db/repositories/alumnos/__init__.py

from .alumnos_repo import AlumnosRepository
from .tutores_repo import TutoresRepository
from .alumnos_tutores_repo import AlumnosTutoresRepository
from .alumnos_hermanos_repo import AlumnosHermanosRepository  # NUEVO
from .autorizaciones_retiro_repo import AutorizacionesRetiroRepository  # NUEVO
from .asistencia_alumnos_repo import AsistenciaAlumnosRepository
from .asistencia_personal_repo import AsistenciaPersonalRepository
from .permisos_personal_repo import PermisosPersonalRepository
from .consentimientos_repo import ConsentimientosRepository
from .alumnos_paralelos_repo import AlumnosParalelosRepository

__all__ = [
    "AlumnosRepository",
    "TutoresRepository",
    "AlumnosTutoresRepository",
    "AlumnosHermanosRepository",  # NUEVO
    "AutorizacionesRetiroRepository",  # NUEVO
    "AsistenciaAlumnosRepository",
    "AsistenciaPersonalRepository",
    "PermisosPersonalRepository",
    "ConsentimientosRepository",
    "AlumnosParalelosRepository",
]
