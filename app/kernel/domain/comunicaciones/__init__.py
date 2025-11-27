# app/kernel/domain/comunicaciones/__init__.py

"""
Módulo de dominio: Comunicaciones

Incluye:
- Conversaciones (chat entre usuarios)
- Mensajes, lecturas y adjuntos
- Notificaciones (campanita)
- Vistas de notificaciones
"""

# Entidades
from .conversacion_entidad import (
    Conversacion,
    Participante,
    EstadoConversacion,
    TipoConversacion,
)
from .mensaje_entidad import Mensaje, TipoMensaje
from .mensaje_lectura_entidad import MensajeLectura  # ← AGREGAR
from .mensaje_adjunto_entidad import MensajeAdjunto, TipoAdjunto
from .notificacion_entidad import (
    Notificacion,
    CanalNotificacion,
    PrioridadNotificacion,
    EstadoNotificacion,
)
from .notificacion_vista_entidad import NotificacionVista

# Errors
from .errors import (
    ComunicacionesError,
    # Conversaciones
    ConversacionNoEncontrada,
    ConversacionCerrada,
    ParticipanteNoAutorizado,
    AsuntoInvalido,
    ParticipantesInsuficientes,
    ParticipanteDuplicado,
    SedeNoCoincide,
    # Mensajes
    MensajeNoEncontrado,
    MensajeInmutable,
    ContenidoInvalido,
    AdjuntoNoEncontrado,
    AdjuntoInvalido,
    ArchivoTamanoExcedido,
    TipoArchivoNoPermitido,
    # Notificaciones
    NotificacionNoEncontrada,
    NotificacionInmutable,
    TituloInvalido,
    CuerpoInvalido,
    TipoNotificacionInvalido,
    CanalNotificacionInvalido,
    NotificacionYaEnviada,
    NotificacionProgramadaCancelada,
)

# Ports
from .ports import (
    # Repositorios
    ConversacionRepositoryPort,
    ParticipanteRepositoryPort,
    MensajeRepositoryPort,
    MensajeLecturaRepositoryPort,
    MensajeAdjuntoRepositoryPort,
    NotificacionRepositoryPort,
    NotificacionVistaRepositoryPort,
    # Servicios externos
    NotificadorServicePort,
    ArchivoStorageServicePort,
    WebSocketServicePort,
    AnalyticsServicePort,
)

__all__ = [
    # Entidades
    "Conversacion",
    "Participante",
    "EstadoConversacion",
    "TipoConversacion",
    "Mensaje",
    "TipoMensaje",
    "MensajeLectura",  # ← AGREGAR
    "MensajeAdjunto",
    "TipoAdjunto",
    "Notificacion",
    "CanalNotificacion",
    "PrioridadNotificacion",
    "EstadoNotificacion",
    "NotificacionVista",
    # Errors
    "ComunicacionesError",
    # Conversaciones
    "ConversacionNoEncontrada",
    "ConversacionCerrada",
    "ParticipanteNoAutorizado",
    "AsuntoInvalido",
    "ParticipantesInsuficientes",
    "ParticipanteDuplicado",
    "SedeNoCoincide",
    # Mensajes
    "MensajeNoEncontrado",
    "MensajeInmutable",
    "ContenidoInvalido",
    "AdjuntoNoEncontrado",
    "AdjuntoInvalido",
    "ArchivoTamanoExcedido",
    "TipoArchivoNoPermitido",
    # Notificaciones
    "NotificacionNoEncontrada",
    "NotificacionInmutable",
    "TituloInvalido",
    "CuerpoInvalido",
    "TipoNotificacionInvalido",
    "CanalNotificacionInvalido",
    "NotificacionYaEnviada",
    "NotificacionProgramadaCancelada",
    # Ports
    "ConversacionRepositoryPort",
    "ParticipanteRepositoryPort",
    "MensajeRepositoryPort",
    "MensajeLecturaRepositoryPort",
    "MensajeAdjuntoRepositoryPort",
    "NotificacionRepositoryPort",
    "NotificacionVistaRepositoryPort",
    "NotificadorServicePort",
    "ArchivoStorageServicePort",
    "WebSocketServicePort",
    "AnalyticsServicePort",
]
