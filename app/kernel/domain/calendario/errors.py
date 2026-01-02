# app/kernel/domain/calendario/errors.py

# ============================================================================
# ERRORES DE TIPOS DE EVENTOS
# ============================================================================

class TipoEventoNoEncontradoError(Exception):
    """Tipo de evento no encontrado"""
    
    def __init__(self, tipo_id: int = None, nombre: str = None):
        if tipo_id:
            message = f"Tipo de evento con ID {tipo_id} no encontrado"
        elif nombre:
            message = f"Tipo de evento '{nombre}' no encontrado"
        else:
            message = "Tipo de evento no encontrado"
        super().__init__(message)


class TipoEventoDuplicadoError(Exception):
    """Ya existe un tipo de evento con ese nombre en la sede"""
    
    def __init__(self, nombre: str, sede_id: int):
        super().__init__(
            f"Ya existe un tipo de evento con nombre '{nombre}' en la sede {sede_id}"
        )


class TipoEventoInactivoError(Exception):
    """Operación no permitida sobre tipo de evento inactivo"""
    
    def __init__(self, tipo_id: int):
        super().__init__(f"El tipo de evento {tipo_id} está inactivo")


class TipoEventoEnUsoError(Exception):
    """No se puede eliminar/desactivar tipo de evento porque tiene eventos asociados"""
    
    def __init__(self, tipo_id: int, cantidad_eventos: int):
        super().__init__(
            f"El tipo de evento {tipo_id} tiene {cantidad_eventos} evento(s) asociado(s) y no puede ser eliminado"
        )


# ============================================================================
# ERRORES DE EVENTOS DEL CALENDARIO
# ============================================================================

class EventoNoEncontradoError(Exception):
    """Evento no encontrado"""
    
    def __init__(self, evento_id: int = None):
        if evento_id:
            message = f"Evento con ID {evento_id} no encontrado"
        else:
            message = "Evento no encontrado"
        super().__init__(message)


class EventoDuplicadoError(Exception):
    """Ya existe un evento similar en la misma fecha"""
    
    def __init__(self, titulo: str, fecha: str, sede_id: int):
        super().__init__(
            f"Ya existe un evento '{titulo}' en la fecha {fecha} para la sede {sede_id}"
        )


class EventoFechaInvalidaError(Exception):
    """Las fechas del evento son inválidas"""
    
    def __init__(self, message: str = "La fecha de fin debe ser posterior o igual a la fecha de inicio"):
        super().__init__(message)


class EventoHoraInvalidaError(Exception):
    """Las horas del evento son inválidas"""
    
    def __init__(self, message: str = "La hora de fin debe ser posterior a la hora de inicio"):
        super().__init__(message)


class EventoFechaFuturaRequeridaError(Exception):
    """El evento debe tener fecha futura"""
    
    def __init__(self):
        super().__init__("No se pueden crear eventos con fechas pasadas")


class EventoPendienteAprobacionError(Exception):
    """El evento requiere aprobación y aún no ha sido aprobado"""
    
    def __init__(self, evento_id: int):
        super().__init__(f"El evento {evento_id} está pendiente de aprobación")


class EventoYaAprobadoError(Exception):
    """El evento ya fue aprobado"""
    
    def __init__(self, evento_id: int):
        super().__init__(f"El evento {evento_id} ya fue aprobado")


class EventoRecordatorioYaEnviadoError(Exception):
    """El recordatorio del evento ya fue enviado"""
    
    def __init__(self, evento_id: int):
        super().__init__(f"El recordatorio del evento {evento_id} ya fue enviado")


class EventoSinPermisosError(Exception):
    """El usuario no tiene permisos para modificar/eliminar este evento"""
    
    def __init__(self, evento_id: int, usuario_id: int):
        super().__init__(
            f"El usuario {usuario_id} no tiene permisos para modificar el evento {evento_id}"
        )


# ============================================================================
# ERRORES DE PLANIFICACIÓN DE ACTIVIDADES
# ============================================================================

class PlanificacionNoEncontradaError(Exception):
    """Planificación de actividad no encontrada"""
    
    def __init__(self, planificacion_id: int = None):
        if planificacion_id:
            message = f"Planificación con ID {planificacion_id} no encontrada"
        else:
            message = "Planificación de actividad no encontrada"
        super().__init__(message)


class PlanificacionDuplicadaError(Exception):
    """Ya existe una planificación en el mismo horario"""
    
    def __init__(self, profesora_id: int, fecha: str, hora_inicio: str, hora_fin: str):
        super().__init__(
            f"La profesora {profesora_id} ya tiene una planificación el {fecha} "
            f"en el horario {hora_inicio} - {hora_fin}"
        )


class PlanificacionHorarioConflictoError(Exception):
    """Conflicto de horarios con otra planificación"""
    
    def __init__(self, fecha: str, hora_inicio: str, hora_fin: str):
        super().__init__(
            f"Existe conflicto de horarios el {fecha} entre {hora_inicio} y {hora_fin}"
        )


class PlanificacionFechaInvalidaError(Exception):
    """La fecha de la planificación es inválida"""
    
    def __init__(self, message: str = "No se pueden planificar actividades en fechas pasadas"):
        super().__init__(message)


class PlanificacionHoraInvalidaError(Exception):
    """Las horas de la planificación son inválidas"""
    
    def __init__(self, message: str = "La hora de fin debe ser posterior a la hora de inicio"):
        super().__init__(message)


class PlanificacionYaCompletadaError(Exception):
    """La planificación ya fue marcada como completada"""
    
    def __init__(self, planificacion_id: int):
        super().__init__(f"La planificación {planificacion_id} ya fue marcada como completada")


class PlanificacionNoCompletadaError(Exception):
    """La planificación aún no ha sido completada"""
    
    def __init__(self, planificacion_id: int):
        super().__init__(f"La planificación {planificacion_id} aún no ha sido completada")


class PlanificacionFueraDePeriodoError(Exception):
    """La planificación está fuera del periodo académico"""
    
    def __init__(self, fecha: str):
        super().__init__(f"La fecha {fecha} está fuera del periodo académico activo")


class PlanificacionSinProfesoraError(Exception):
    """La planificación debe tener una profesora asignada"""
    
    def __init__(self):
        super().__init__("La planificación debe tener una profesora responsable asignada")


class PlanificacionSinPermisosError(Exception):
    """El usuario no tiene permisos para modificar esta planificación"""
    
    def __init__(self, planificacion_id: int, usuario_id: int):
        super().__init__(
            f"El usuario {usuario_id} no tiene permisos para modificar la planificación {planificacion_id}"
        )


# ============================================================================
# ERRORES DE VALIDACIÓN GENERAL
# ============================================================================

class CalendarioFechaInvalidaError(Exception):
    """Fecha inválida para operaciones de calendario"""
    
    def __init__(self, campo: str, mensaje: str):
        super().__init__(f"Error en {campo}: {mensaje}")


class CalendarioHorarioInvalidoError(Exception):
    """Horario inválido para operaciones de calendario"""
    
    def __init__(self, campo: str, mensaje: str):
        super().__init__(f"Error en {campo}: {mensaje}")


class CalendarioDatosInvalidosError(Exception):
    """Datos proporcionados inválidos"""
    
    def __init__(self, campo: str, mensaje: str):
        super().__init__(f"Error en {campo}: {mensaje}")


class CalendarioCampoRequeridoError(Exception):
    """Campo requerido faltante"""
    
    def __init__(self, campo: str):
        super().__init__(f"El campo '{campo}' es requerido")


class CalendarioColorInvalidoError(Exception):
    """Color hexadecimal inválido"""
    
    def __init__(self, color: str):
        super().__init__(f"El color '{color}' no es un código hexadecimal válido (formato: #RRGGBB)")


class CalendarioSedeNoCoincideError(Exception):
    """La sede del evento/planificación no coincide con la sede del tipo de evento"""
    
    def __init__(self, sede_evento: int, sede_tipo: int):
        super().__init__(
            f"La sede del evento ({sede_evento}) no coincide con la sede del tipo de evento ({sede_tipo})"
        )


# ============================================================================
# ERRORES DE PERMISOS
# ============================================================================

class CalendarioPermisosDenegadosError(Exception):
    """Permisos insuficientes para realizar la operación"""
    
    def __init__(self, operacion: str, rol_requerido: str = None):
        if rol_requerido:
            message = f"Se requiere rol '{rol_requerido}' para {operacion}"
        else:
            message = f"Permisos insuficientes para {operacion}"
        super().__init__(message)


class CalendarioNoEsProfesoraError(Exception):
    """El usuario no es profesora y no puede realizar esta acción"""
    
    def __init__(self, usuario_id: int):
        super().__init__(f"El usuario {usuario_id} no es profesora")


class CalendarioNoEsDirectoraError(Exception):
    """El usuario no es directora y no puede realizar esta acción"""
    
    def __init__(self, usuario_id: int):
        super().__init__(f"El usuario {usuario_id} no es directora o admin")


# ============================================================================
# ERRORES DE RELACIONES
# ============================================================================

class CalendarioParaleloNoEncontradoError(Exception):
    """Paralelo no encontrado"""
    
    def __init__(self, paralelo_id: int):
        super().__init__(f"Paralelo con ID {paralelo_id} no encontrado")


class CalendarioProfesoraNoEncontradaError(Exception):
    """Profesora no encontrada"""
    
    def __init__(self, profesora_id: int):
        super().__init__(f"Profesora con ID {profesora_id} no encontrada")


class CalendarioSedeNoEncontradaError(Exception):
    """Sede no encontrada"""
    
    def __init__(self, sede_id: int):
        super().__init__(f"Sede con ID {sede_id} no encontrada")


class CalendarioRelacionInvalidaError(Exception):
    """Relación inválida entre entidades"""
    
    def __init__(self, entidad_tipo: str, entidad_id: int, mensaje: str):
        super().__init__(f"Relación inválida con {entidad_tipo} {entidad_id}: {mensaje}")
