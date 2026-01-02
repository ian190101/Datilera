# app/infrastructure/services/websocket_service.py

from app.kernel.domain.comunicaciones import Mensaje, WebSocketServicePort
from app.infrastructure.ws.manager import ws_manager
from app.infrastructure.ws.events import (
    WSChatMessagePayload,
    build_chat_message_event,
)


class WebSocketService(WebSocketServicePort):
    """Implementación real del servicio WebSocket para chat."""

    async def notificar_nuevo_mensaje(
        self,
        conversacion_id: int,
        mensaje: Mensaje,
    ) -> None:
        payload = WSChatMessagePayload(
            mensaje_id=mensaje.id,
            conversacion_id=conversacion_id,
            remitente_id=mensaje.remitente_id,
            texto=mensaje.contenido,
            enviado_en=mensaje.enviado_en.isoformat(),
        )
        event = build_chat_message_event(payload)

        # Por ahora: solo al remitente. Cuando conectemos participantes,
        # aquí iteraremos por todos los user_id de la conversación.
        await ws_manager.send_to_user(mensaje.remitente_id, event)

    async def notificar_lectura(
        self,
        conversacion_id: int,
        mensaje_id: int,
        usuario_id: int,
    ) -> None:
        # Lo dejaremos para cuando implementemos “marcar leído” con WS.
        return None

    async def notificar_escribiendo(
        self,
        conversacion_id: int,
        usuario_id: int,
        escribiendo: bool,
    ) -> None:
        # Se implementará cuando hagamos el “typing indicator”.
        return None
