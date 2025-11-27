# app/infrastructure/db/models/alumnos/__init__.py

from .alumnos import Alumno
from .alumnos_paralelos import AlumnoParalelo
from .asistencia_alumnos import AsistenciaAlumno
from .asistencia_personal import AsistenciaPersonal
from .permisos_personal import PermisoPersonal
from .consentimientos import Consentimiento
from .tutores import Tutor  # NUEVO
from .alumnos_tutores import AlumnoTutor  # NUEVO
from .alumnos_hermanos import AlumnoHermano  # NUEVO
from .autorizaciones_retiro import AutorizacionRetiro  # NUEVO


__all__ = [
    "Alumno",
    "AlumnoParalelo",
    "AsistenciaAlumno",
    "AsistenciaPersonal",
    "PermisoPersonal",
    "Consentimiento",
    "Tutor",  # NUEVO
    "AlumnoTutor",  # NUEVO
    "AlumnoHermano",  # NUEVO
    "AutorizacionRetiro",  # NUEVO
]
