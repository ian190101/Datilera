# app/kernel/application/comunicaciones/conversaciones/cerrar_conversacion.py

from app.kernel.domain.comunicaciones import (
    ConversacionRepositoryPort,
    ParticipanteRepositoryPort,
    ConversacionNoEncontrada,
    ParticipanteNoAutorizado,
)


class CerrarConversacionUseCase:
    """Caso de uso: Cerrar conversación (US-COM-006).
    
    Reglas:
    - Solo participantes pueden cerrar
    - Bloquea nuevos mensajes
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
    ) -> None:
        """Cierra una conversación.
        
        Args:
            conversacion_id: ID de la conversación
            usuario_id: Usuario que cierra
            
        Raises:
            ConversacionNoEncontrada: Si no existe
            ParticipanteNoAutorizado: Si no es participante
        """
        # Verificar existencia
        conversacion = await self.conversacion_repo.obtener_por_id(conversacion_id)
        if not conversacion:
            raise ConversacionNoEncontrada(conversacion_id)

        # Verificar participación
        es_participante = await self.participante_repo.es_participante(
            conversacion_id, usuario_id
        )
        if not es_participante:
            raise ParticipanteNoAutorizado(usuario_id, conversacion_id)

        # Cerrar
        await self.conversacion_repo.cerrar(conversacion_id, usuario_id)
