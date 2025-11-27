# app/infrastructure/services/websocket_service_mock.py

from app.kernel.domain.comunicaciones import Mensaje, WebSocketServicePort


class WebSocketServiceMock(WebSocketServicePort):
    """Mock del servicio WebSocket para desarrollo."""

    async def notificar_nuevo_mensaje(
        self, conversacion_id: int, mensaje: Mensaje
    ) -> None:
        """Mock: No hace nada por ahora."""
        print(f"[WS Mock] Nuevo mensaje en conversación {conversacion_id}: {mensaje.id}")
        pass

    async def notificar_lectura(
        self, conversacion_id: int, mensaje_id: int, usuario_id: int
    ) -> None:
        """Mock: No hace nada por ahora."""
        print(f"[WS Mock] Mensaje {mensaje_id} leído por usuario {usuario_id}")
        pass

    async def notificar_escribiendo(
        self, conversacion_id: int, usuario_id: int, escribiendo: bool
    ) -> None:
        """Mock: No hace nada por ahora."""
        print(f"[WS Mock] Usuario {usuario_id} escribiendo: {escribiendo}")
        pass
