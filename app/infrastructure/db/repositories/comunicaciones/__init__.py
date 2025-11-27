# app/infrastructure/db/repositories/comunicaciones/__init__.py
from .conversaciones_repo import ConversacionesRepository
from .conversaciones_participantes_repo import ConversacionesParticipantesRepository  # ← AGREGAR
from .mensajes_repo import MensajesRepository
from .mensajes_adjuntos_repo import MensajesAdjuntosRepository
from .mensajes_lectura_repo import MensajesLecturasRepository  # ← AGREGAR
from .notificaciones_repo import NotificacionesRepository
from .notificacion_vistas_repo import NotificacionVistasRepository

__all__ = [
    "ConversacionesRepository",
    "ConversacionesParticipantesRepository",  # ← AGREGAR
    "MensajesRepository",
    "MensajesAdjuntosRepository",
    "MensajesLecturasRepository",  # ← AGREGAR
    "NotificacionesRepository",
    "NotificacionVistasRepository",
]
