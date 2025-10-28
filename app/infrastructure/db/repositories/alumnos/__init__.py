# app/infrastructure/db/repositories/alumnos/__init__.py
from .alumnos_repo import AlumnosRepository
from .alumnos_paralelos_repo import AlumnosParalelosRepository
from .asistencia_alumnos_repo import AsistenciaAlumnosRepository
from .asistencia_personal_repo import AsistenciaPersonalRepository
from .consentimientos_repo import ConsentimientosRepository
from .permisos_personal_repo import PermisosPersonalRepository

__all__ = [
    "AlumnosRepository", "AlumnosParalelosRepository",
    "AsistenciaAlumnosRepository", "AsistenciaPersonalRepository",
    "ConsentimientosRepository", "PermisosPersonalRepository",
]
