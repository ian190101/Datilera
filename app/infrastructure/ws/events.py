from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WSEventType(str, Enum):
    NOTIFICATION_NEW = "notification.new"
    NOTIFICATION_READ = "notification.read"
    CHAT_MESSAGE_NEW = "chat.message"
    CHAT_TYPING = "chat.typing"
    CHAT_STOP_TYPING = "chat.stop_typing"
    SYSTEM_EVENT = "system.event"
    NOTIF_BADGE = "notif_badge"  # nuevo



class WSBaseEvent(BaseModel):
    type: WSEventType = Field(..., description="Tipo de evento WebSocket")
    data: Dict[str, Any] = Field(..., description="Payload específico del evento")


class WSNotificationNewPayload(BaseModel):
    notificacion_id: int
    titulo: str
    mensaje: str
    tipo: str
    prioridad: str = "media"
    creado_en: str
    leida: bool
    sede_id: int


class WSNotificationReadPayload(BaseModel):
    notificacion_id: int
    sede_id: int


class WSChatMessagePayload(BaseModel):
    mensaje_id: int
    conversacion_id: int
    remitente_id: int
    texto: str
    enviado_en: str

class NotifBadgeEvent:
    usuario_id: int
    sede_id: int
    total_no_leidas: int


def build_notification_new_event(payload: WSNotificationNewPayload) -> WSBaseEvent:
    return WSBaseEvent(
        type=WSEventType.NOTIFICATION_NEW,
        data=payload.model_dump(),
    )


def build_notification_read_event(payload: WSNotificationReadPayload) -> WSBaseEvent:
    return WSBaseEvent(
        type=WSEventType.NOTIFICATION_READ,
        data=payload.model_dump(),
    )


def build_chat_message_event(payload: WSChatMessagePayload) -> WSBaseEvent:
    return WSBaseEvent(
        type=WSEventType.CHAT_MESSAGE_NEW,
        data=payload.model_dump(),
    )
