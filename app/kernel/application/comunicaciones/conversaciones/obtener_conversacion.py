# app/kernel/application/comunicaciones/conversaciones/obtener_conversacion.py

from app.kernel.domain.comunicaciones import (
    Conversacion,
    ConversacionRepositoryPort,
    ParticipanteRepositoryPort,
    ConversacionNoEncontrada,
    ParticipanteNoAutorizado,
)


class ObtenerConversacionUseCase:
    """Caso de uso: Obtener detalle de conversación.
    
    Reglas:
    - Solo participantes pueden ver la conversación
    """

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
        usuario_id: int,
    ) -> Conversacion:
        """Obtiene una conversación por ID.
        
        Args:
            conversacion_id: ID de la conversación
            usuario_id: Usuario que solicita
            
        Returns:
            Conversación encontrada
            
        Raises:
            ConversacionNoEncontrada: Si no existe
            ParticipanteNoAutorizado: Si no es participante
        """
        # Obtener conversación
        conversacion = await self.conversacion_repo.obtener_por_id(conversacion_id)
        if not conversacion:
            raise ConversacionNoEncontrada(conversacion_id)

        # Verificar que es participante
        es_participante = await self.participante_repo.es_participante(
            conversacion_id, usuario_id
        )
        if not es_participante:
            raise ParticipanteNoAutorizado(usuario_id, conversacion_id)

        return conversacion
