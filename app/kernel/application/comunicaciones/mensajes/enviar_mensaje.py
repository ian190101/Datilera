# app/kernel/application/comunicaciones/mensajes/enviar_mensaje.py

from typing import Dict, Optional
from app.kernel.domain.comunicaciones import (
    Mensaje,
    TipoMensaje,
    ConversacionRepositoryPort,
    ParticipanteRepositoryPort,
    MensajeRepositoryPort,
    WebSocketServicePort,
    ConversacionNoEncontrada,
    ParticipanteNoAutorizado,
    ConversacionCerrada,
)


class EnviarMensajeUseCase:
    """Caso de uso: Enviar mensaje en conversación (US-COM-002).
    
    Reglas:
    - Solo participantes pueden enviar
    - Conversación debe estar abierta
    - Contenido obligatorio (≤4000 chars)
    - Notifica en tiempo real vía WebSocket
    - Actualiza ultima_actividad_en
    """

    def __init__(
        self,
        conversacion_repo: ConversacionRepositoryPort,
        participante_repo: ParticipanteRepositoryPort,
        mensaje_repo: MensajeRepositoryPort,
        websocket_service: WebSocketServicePort,
    ):
        self.conversacion_repo = conversacion_repo
        self.participante_repo = participante_repo
        self.mensaje_repo = mensaje_repo
        self.websocket_service = websocket_service

    async def ejecutar(
        self,
        conversacion_id: int,
        remitente_id: int,
        contenido: str,
        tipo: TipoMensaje = TipoMensaje.TEXTO,
        reply_a_id: Optional[int] = None,
        metadatos: Optional[Dict] = None,
    ) -> Mensaje:
        """Envía un mensaje en una conversación.
        
        Args:
            conversacion_id: ID de la conversación
            remitente_id: Usuario que envía
            contenido: Contenido del mensaje (obligatorio, ≤4000)
            tipo: Tipo de mensaje (texto/sistema)
            reply_a_id: ID del mensaje al que responde (opcional)
            metadatos: Datos adicionales (opcional)
            
        Returns:
            Mensaje creado
            
        Raises:
            ConversacionNoEncontrada: Si no existe
            ParticipanteNoAutorizado: Si remitente no es participante
            ConversacionCerrada: Si la conversación está cerrada
            ContenidoInvalido: Si contenido vacío o excede límite
        """
        # Verificar conversación existe
        conversacion = await self.conversacion_repo.obtener_por_id(conversacion_id)
        if not conversacion:
            raise ConversacionNoEncontrada(conversacion_id)

        # Verificar que está abierta
        if conversacion.esta_cerrada():
            raise ConversacionCerrada(conversacion_id)

        # Verificar que es participante
        es_participante = await self.participante_repo.es_participante(
            conversacion_id, remitente_id
        )
        if not es_participante:
            raise ParticipanteNoAutorizado(remitente_id, conversacion_id)

        # Crear mensaje (validaciones en entidad)
        mensaje = await self.mensaje_repo.crear(
            conversacion_id=conversacion_id,
            remitente_id=remitente_id,
            contenido=contenido,
            tipo=tipo,
            reply_a_id=reply_a_id,
            metadatos=metadatos,
        )

        # Actualizar ultima_actividad_en
        await self.conversacion_repo.touch(conversacion_id)

        # Notificar en tiempo real vía WebSocket
        await self.websocket_service.notificar_nuevo_mensaje(
            conversacion_id=conversacion_id,
            mensaje=mensaje,
        )

        return mensaje
