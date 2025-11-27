# app/kernel/application/comunicaciones/conversaciones/remover_participante.py

from app.kernel.domain.comunicaciones import (
    ConversacionRepositoryPort,
    ParticipanteRepositoryPort,
    ConversacionNoEncontrada,
    ParticipanteNoAutorizado,
)


class RemoverParticipanteUseCase:
    """Caso de uso: Remover participante de conversación."""

    def __init__(
        self,
        conversacion_repo: ConversacionRepositoryPort,
        participante_repo: ParticipanteRepositoryPort,
    ):
        self.conversacion_repo = conversacion_repo
        self.participante_repo = participante_repo

    async def ejecutar(
        self,
        conversacion_id: int,
        usuario_solicitante_id: int,
        usuario_a_remover_id: int,
    ) -> bool:
        """Remueve un participante de la conversación.
        
        Args:
            conversacion_id: ID de la conversación
            usuario_solicitante_id: Usuario que remueve
            usuario_a_remover_id: Usuario a remover
            
        Returns:
            True si se removió, False si no era participante
            
        Raises:
            ConversacionNoEncontrada: Si no existe
            ParticipanteNoAutorizado: Si solicitante no es participante
        """
        # Verificar conversación existe
        conversacion = await self.conversacion_repo.obtener_por_id(conversacion_id)
        if not conversacion:
            raise ConversacionNoEncontrada(conversacion_id)

        # Verificar que solicitante es participante
        es_participante = await self.participante_repo.es_participante(
            conversacion_id, usuario_solicitante_id
        )
        if not es_participante:
            raise ParticipanteNoAutorizado(usuario_solicitante_id, conversacion_id)

        # Remover
        removido = await self.participante_repo.remover(conversacion_id, usuario_a_remover_id)
        
        if removido:
            # Touch para actualizar ultima_actividad
            await self.conversacion_repo.touch(conversacion_id)
        
        return removido
