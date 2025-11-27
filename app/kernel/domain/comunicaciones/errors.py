# app/kernel/domain/comunicaciones/errors.py

"""
Excepciones de dominio para Comunicaciones.
"""

class ComunicacionesError(Exception):
    """Base de errores de Comunicaciones."""
    pass


# ==========================================
# Conversaciones
# ==========================================

class ConversacionNoEncontrada(ComunicacionesError):
    def __init__(self, conversacion_id: int):
        super().__init__(f"Conversación {conversacion_id} no encontrada")


class ConversacionCerrada(ComunicacionesError):
    def __init__(self, conversacion_id: int):
        super().__init__(f"Conversación {conversacion_id} está cerrada y no permite operaciones")


class ParticipanteNoAutorizado(ComunicacionesError):
    def __init__(self, usuario_id: int, conversacion_id: int):
        super().__init__(
            f"Usuario {usuario_id} no es participante de la conversación {conversacion_id}"
        )


class AsuntoInvalido(ComunicacionesError):
    def __init__(self, razon: str):
        super().__init__(f"Asunto inválido: {razon}")


class ParticipantesInsuficientes(ComunicacionesError):
    def __init__(self, cantidad: int):
        super().__init__(
            f"Se requieren al menos 2 participantes, se proporcionaron {cantidad}"
        )


class ParticipanteDuplicado(ComunicacionesError):
    def __init__(self, usuario_id: int, conversacion_id: int):
        super().__init__(
            f"Usuario {usuario_id} ya es participante de la conversación {conversacion_id}"
        )


class SedeNoCoincide(ComunicacionesError):
    def __init__(self, recurso: str, sede_esperada: int, sede_recurso: int):
        super().__init__(
            f"La sede del {recurso} ({sede_recurso}) no coincide con la esperada ({sede_esperada})"
        )


# ==========================================
# Mensajes
# ==========================================

class MensajeNoEncontrado(ComunicacionesError):
    def __init__(self, mensaje_id: int):
        super().__init__(f"Mensaje {mensaje_id} no encontrado")


class MensajeInmutable(ComunicacionesError):
    def __init__(self, mensaje_id: int, operacion: str):
        super().__init__(
            f"Los mensajes son inmutables: no se puede '{operacion}' el mensaje {mensaje_id}"
        )


class ContenidoInvalido(ComunicacionesError):
    def __init__(self, razon: str):
        super().__init__(f"Contenido inválido: {razon}")


class AdjuntoNoEncontrado(ComunicacionesError):
    def __init__(self, adjunto_id: int):
        super().__init__(f"Adjunto {adjunto_id} no encontrado")


class AdjuntoInvalido(ComunicacionesError):
    def __init__(self, razon: str):
        super().__init__(f"Adjunto inválido: {razon}")


class ArchivoTamanoExcedido(ComunicacionesError):
    def __init__(self, tamano: int, maximo: int):
        super().__init__(
            f"El archivo pesa {tamano} bytes y excede el límite {maximo} bytes"
        )


class TipoArchivoNoPermitido(ComunicacionesError):
    def __init__(self, tipo: str):
        super().__init__(f"Tipo de archivo no permitido: {tipo}")


# ==========================================
# Notificaciones
# ==========================================

class NotificacionNoEncontrada(ComunicacionesError):
    def __init__(self, notificacion_id: int):
        super().__init__(f"Notificación {notificacion_id} no encontrada")


class NotificacionInmutable(ComunicacionesError):
    def __init__(self, notificacion_id: int):
        super().__init__(
            f"Las notificaciones son inmutables: no se puede eliminar la notificación {notificacion_id}"
        )


class TituloInvalido(ComunicacionesError):
    def __init__(self, razon: str):
        super().__init__(f"Título inválido: {razon}")


class CuerpoInvalido(ComunicacionesError):
    def __init__(self, razon: str):
        super().__init__(f"Cuerpo inválido: {razon}")


class TipoNotificacionInvalido(ComunicacionesError):
    def __init__(self, tipo: str):
        super().__init__(f"Tipo de notificación inválido: {tipo}")


class CanalNotificacionInvalido(ComunicacionesError):
    def __init__(self, canal: str):
        super().__init__(f"Canal de notificación inválido: {canal}")


class NotificacionYaEnviada(ComunicacionesError):
    def __init__(self, notificacion_id: int):
        super().__init__(f"Notificación {notificacion_id} ya fue enviada")


class NotificacionProgramadaCancelada(ComunicacionesError):
    def __init__(self, notificacion_id: int):
        super().__init__(f"Notificación programada {notificacion_id} ya fue cancelada")
