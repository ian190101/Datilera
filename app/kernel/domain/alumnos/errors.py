# app/kernel/domain/alumnos/errors.py

class AlumnosError(Exception):
    """Base para errores del subdominio Alumnos."""
    pass


class AlumnoNoEncontrado(AlumnosError):
    pass


class CupoExcedido(AlumnosError):
    """Se superó el cupo permitido para el paralelo."""
    pass


class TrasladoInvalido(AlumnosError):
    """Transferencia con solapamiento de vigencias u otras reglas."""
    pass


class AsistenciaDuplicada(AlumnosError):
    """Ya existe asistencia para (alumno, fecha)."""
    pass


class AsistenciaInvalida(AlumnosError):
    """Estado/hora_retraso inválidos o fuera de reglas."""
    pass
class ConsentimientoInvalido(AlumnosError):
    pass


class PermisoNoEncontrado(AlumnosError):
    pass


class PermisoNoPendiente(AlumnosError):
    """Intento de aprobar/rechazar un permiso que no está PENDIENTE."""
    pass