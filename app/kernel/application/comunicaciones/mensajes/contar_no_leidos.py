# app/kernel/application/comunicaciones/mensajes/contar_no_leidos.py

from app.kernel.domain.comunicaciones import (
    ConversacionRepositoryPort,
    ParticipanteRepositoryPort,
    MensajeRepositoryPort,
    ConversacionNoEncontrada,
    ParticipanteNoAutorizado,
)


class ContarNoLeidosUseCase:
    """Caso de uso: Contar mensajes no leídos en conversación (US-COM-003)."""

    def __init__(
        self,
        conversacion_repo: ConversacionRepositoryPort,
        participante_repo: ParticipanteRepositoryPort,
        mensaje_repo: MensajeRepositoryPort,
    ):
        self.conversacion_repo = conversacion_repo
        self.participante_repo = participante_repo
        self.mensaje_repo = mensaje_repo

    async def ejecutar(
        self,
        conversacion_id: int,
        usuario_id: int,
    ) -> int:
        """Cuenta mensajes no leídos en una conversación.
        
        Args:
            conversacion_id: ID de la conversación
            usuario_id: Usuario que consulta
            
        Returns:
            Cantidad de mensajes no leídos
            
        Raises:
            ConversacionNoEncontrada: Si no existe
            ParticipanteNoAutorizado: Si no es participante
        """
        # Verificar conversación existe
        conversacion = await self.conversacion_repo.obtener_por_id(conversacion_id)
        if not conversacion:
            raise ConversacionNoEncontrada(conversacion_id)

        # Verificar que es participante
        es_participante = await self.participante_repo.es_participante(
            conversacion_id, usuario_id
        )
        if not es_participante:
            raise ParticipanteNoAutorizado(usuario_id, conversacion_id)

        # Contar no leídos
        return await self.mensaje_repo.contar_no_leidos_conversacion(
            conversacion_id=conversacion_id,
            usuario_id=usuario_id,
        )
