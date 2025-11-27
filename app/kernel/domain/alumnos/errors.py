# app/domain/errors/alumnos/errors.py

# ============================================================================
# ERRORES DE ALUMNOS
# ============================================================================

class AlumnoNoEncontradoError(Exception):
    """Alumno no encontrado"""
    def __init__(self, alumno_id: int = None, codigo: str = None, documento: str = None):
        if alumno_id:
            message = f"Alumno con ID {alumno_id} no encontrado"
        elif codigo:
            message = f"Alumno con código '{codigo}' no encontrado"
        elif documento:
            message = f"Alumno con documento '{documento}' no encontrado"
        else:
            message = "Alumno no encontrado"
        super().__init__(message)


class AlumnoDuplicadoError(Exception):
    """Alumno ya existe con ese documento o código"""
    def __init__(self, campo: str, valor: str):
        super().__init__(f"Ya existe un alumno con {campo}: {valor}")


class AlumnoInactivoError(Exception):
    """Operación no permitida sobre alumno inactivo"""
    def __init__(self, alumno_id: int):
        super().__init__(f"El alumno {alumno_id} está inactivo")


class AlumnoMenorEdadError(Exception):
    """El alumno no cumple con la edad mínima"""
    def __init__(self, edad_actual: int, edad_minima: int):
        super().__init__(
            f"El alumno tiene {edad_actual} años, se requiere mínimo {edad_minima} años"
        )


# ============================================================================
# ERRORES DE TUTORES
# ============================================================================

class TutorNoEncontradoError(Exception):
    """Tutor no encontrado"""
    def __init__(self, tutor_id: int = None, documento: str = None):
        if tutor_id:
            message = f"Tutor con ID {tutor_id} no encontrado"
        elif documento:
            message = f"Tutor con documento '{documento}' no encontrado"
        else:
            message = "Tutor no encontrado"
        super().__init__(message)


class TutorDuplicadoError(Exception):
    """Tutor ya existe con ese documento"""
    def __init__(self, documento: str):
        super().__init__(f"Ya existe un tutor con documento: {documento}")


class TutorSinAlumnosError(Exception):
    """El tutor no tiene alumnos asignados"""
    def __init__(self, tutor_id: int):
        super().__init__(f"El tutor {tutor_id} no tiene alumnos asignados")


# ============================================================================
# ERRORES DE RELACIÓN ALUMNO-TUTOR
# ============================================================================

class RelacionAlumnoTutorNoEncontradaError(Exception):
    """Relación alumno-tutor no encontrada"""
    def __init__(self, alumno_id: int = None, tutor_id: int = None):
        if alumno_id and tutor_id:
            message = f"No existe relación entre alumno {alumno_id} y tutor {tutor_id}"
        else:
            message = "Relación alumno-tutor no encontrada"
        super().__init__(message)


class RelacionAlumnoTutorDuplicadaError(Exception):
    """Ya existe una relación entre el alumno y el tutor"""
    def __init__(self, alumno_id: int, tutor_id: int):
        super().__init__(f"Ya existe una relación entre alumno {alumno_id} y tutor {tutor_id}")


class TutorPrincipalDuplicadoError(Exception):
    """El alumno ya tiene un tutor principal"""
    def __init__(self, alumno_id: int):
        super().__init__(f"El alumno {alumno_id} ya tiene un tutor principal asignado")


# ============================================================================
# ERRORES DE HERMANOS
# ============================================================================

class HermanoNoEncontradoError(Exception):
    """Hermano no encontrado"""
    def __init__(self, hermano_id: int):
        super().__init__(f"Hermano con ID {hermano_id} no encontrado")


# ============================================================================
# ERRORES DE AUTORIZACIONES DE RETIRO
# ============================================================================

class AutorizacionRetiroNoEncontradaError(Exception):
    """Autorización de retiro no encontrada"""
    def __init__(self, autorizacion_id: int = None, ci: str = None):
        if autorizacion_id:
            message = f"Autorización con ID {autorizacion_id} no encontrada"
        elif ci:
            message = f"No hay autorización activa para CI: {ci}"
        else:
            message = "Autorización de retiro no encontrada"
        super().__init__(message)


class AutorizacionRetiroDuplicadaError(Exception):
    """Ya existe una autorización activa para este CI"""
    def __init__(self, alumno_id: int, ci: str):
        super().__init__(
            f"Ya existe una autorización activa para el alumno {alumno_id} con CI: {ci}"
        )


class AutorizacionRetiroInactivaError(Exception):
    """La autorización está inactiva"""
    def __init__(self, autorizacion_id: int):
        super().__init__(f"La autorización {autorizacion_id} está inactiva")


# ============================================================================
# ERRORES DE ASISTENCIA
# ============================================================================

class AsistenciaNoEncontradaError(Exception):
    """Registro de asistencia no encontrado"""
    def __init__(self, asistencia_id: int = None):
        if asistencia_id:
            message = f"Asistencia con ID {asistencia_id} no encontrada"
        else:
            message = "Registro de asistencia no encontrado"
        super().__init__(message)


class AsistenciaDuplicadaError(Exception):
    """Ya existe un registro de asistencia para esta fecha"""
    def __init__(self, entidad: str, entidad_id: int, fecha: str):
        super().__init__(
            f"Ya existe un registro de asistencia para {entidad} {entidad_id} en la fecha {fecha}"
        )


class AsistenciaFechaFuturaError(Exception):
    """No se puede registrar asistencia de fechas futuras"""
    def __init__(self):
        super().__init__("No se puede registrar asistencia de fechas futuras")


# ============================================================================
# ERRORES DE PERMISOS
# ============================================================================

class PermisoNoEncontradoError(Exception):
    """Permiso no encontrado"""
    def __init__(self, permiso_id: int):
        super().__init__(f"Permiso con ID {permiso_id} no encontrado")


class PermisoYaAprobadoError(Exception):
    """El permiso ya fue aprobado o rechazado"""
    def __init__(self, permiso_id: int, estado_actual: str):
        super().__init__(f"El permiso {permiso_id} ya fue {estado_actual}")


class PermisoFechasInvalidasError(Exception):
    """Las fechas del permiso son inválidas"""
    def __init__(self, message: str = "La fecha de fin debe ser posterior a la fecha de inicio"):
        super().__init__(message)


# ============================================================================
# ERRORES DE CONSENTIMIENTOS
# ============================================================================

class ConsentimientoNoEncontradoError(Exception):
    """Consentimiento no encontrado"""
    def __init__(self, alumno_id: int):
        super().__init__(f"No hay consentimientos registrados para el alumno {alumno_id}")


# ============================================================================
# ERRORES DE ASIGNACIÓN PARALELO
# ============================================================================

class AsignacionParaleloNoEncontradaError(Exception):
    """Asignación alumno-paralelo no encontrada"""
    def __init__(self, asignacion_id: int):
        super().__init__(f"Asignación con ID {asignacion_id} no encontrada")


class AsignacionParaleloDuplicadaError(Exception):
    """El alumno ya está asignado a este paralelo"""
    def __init__(self, alumno_id: int, paralelo_id: int):
        super().__init__(f"El alumno {alumno_id} ya está asignado al paralelo {paralelo_id}")


# ============================================================================
# ERRORES GENERALES DE VALIDACIÓN
# ============================================================================

class DatosInvalidosError(Exception):
    """Datos proporcionados inválidos"""
    def __init__(self, campo: str, mensaje: str):
        super().__init__(f"Error en {campo}: {mensaje}")


class CampoRequeridoError(Exception):
    """Campo requerido faltante"""
    def __init__(self, campo: str):
        super().__init__(f"El campo '{campo}' es requerido")
