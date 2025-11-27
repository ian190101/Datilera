# app/kernel/application/comunicaciones/mensajes/marcar_mensaje_leido.py

from app.kernel.domain.comunicaciones import (
    MensajeRepositoryPort,
    ParticipanteRepositoryPort,
    MensajeLecturaRepositoryPort,
    WebSocketServicePort,
    MensajeNoEncontrado,
    ParticipanteNoAutorizado,
)


class MarcarMensajeLeidoUseCase:
    """Caso de uso: Marcar mensaje como leído (US-COM-003).
    
    Reglas:
    - Solo participantes pueden marcar
    - Notifica en tiempo real vía WebSocket
    - Idempotente (no falla si ya está leído)
    """

    def __init__(
        self,
        mensaje_repo: MensajeRepositoryPort,
        participante_repo: ParticipanteRepositoryPort,
        lectura_repo: MensajeLecturaRepositoryPort,
        websocket_service: WebSocketServicePort,
    ):
        self.mensaje_repo = mensaje_repo
        self.participante_repo = participante_repo
        self.lectura_repo = lectura_repo
        self.websocket_service = websocket_service

    async def ejecutar(
        self,
        mensaje_id: int,
        usuario_id: int,
    ) -> None:
        """Marca un mensaje como leído.
        
        Args:
            mensaje_id: ID del mensaje
            usuario_id: Usuario que marca como leído
            
        Raises:
            MensajeNoEncontrado: Si no existe
            ParticipanteNoAutorizado: Si no es participante
        """
        # Verificar mensaje existe
        mensaje = await self.mensaje_repo.obtener_por_id(mensaje_id)
        if not mensaje:
            raise MensajeNoEncontrado(mensaje_id)

        # Verificar que es participante
        es_participante = await self.participante_repo.es_participante(
            mensaje.conversacion_id, usuario_id
        )
        if not es_participante:
            raise ParticipanteNoAutorizado(usuario_id, mensaje.conversacion_id)

        # No marcar si es el remitente
        if mensaje.remitente_id == usuario_id:
            return

        # Verificar si ya está leído (idempotencia)
        ya_leido = await self.lectura_repo.ya_leido(mensaje_id, usuario_id)
        if ya_leido:
            return

        # Marcar como leído
        await self.lectura_repo.marcar_leido(mensaje_id, usuario_id)

        # Notificar en tiempo real
        await self.websocket_service.notificar_lectura(
            conversacion_id=mensaje.conversacion_id,
            mensaje_id=mensaje_id,
            usuario_id=usuario_id,
        )
