from .alumnos import Alumno
from .alumnos_paralelos import AlumnoParalelo
from .asistencia_alumnos import AsistenciaAlumno, EstadoAsistenciaAlumno
from .asistencia_personal import AsistenciaPersonal, EstadoAsistenciaPersonal
from .consentimientos import Consentimiento
from .permisos_personal import PermisoPersonal, EstadoPermiso

__all__ = [
    "Alumno",
    "AlumnoParalelo",
    "AsistenciaAlumno",
    "EstadoAsistenciaAlumno",
    "AsistenciaPersonal",
    "EstadoAsistenciaPersonal",
    "Consentimiento",
    "PermisoPersonal",
    "EstadoPermiso",
]
