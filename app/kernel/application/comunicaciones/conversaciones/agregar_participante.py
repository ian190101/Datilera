# app/kernel/application/comunicaciones/conversaciones/agregar_participante.py

from app.kernel.domain.comunicaciones import (
    Participante,
    ConversacionRepositoryPort,
    ParticipanteRepositoryPort,
    ConversacionNoEncontrada,
    ParticipanteNoAutorizado,
    ParticipanteDuplicado,
)


class AgregarParticipanteUseCase:
    """Caso de uso: Agregar participante a conversación."""

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
        nuevo_participante: Participante,
    ) -> None:
        """Agrega un participante a la conversación.
        
        Args:
            conversacion_id: ID de la conversación
            usuario_solicitante_id: Usuario que agrega
            nuevo_participante: Participante a agregar
            
        Raises:
            ConversacionNoEncontrada: Si no existe
            ParticipanteNoAutorizado: Si solicitante no es participante
            ParticipanteDuplicado: Si ya es participante
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

        # Verificar que no esté duplicado
        ya_participante = await self.participante_repo.es_participante(
            conversacion_id, nuevo_participante.usuario_id
        )
        if ya_participante:
            raise ParticipanteDuplicado(nuevo_participante.usuario_id, conversacion_id)

        # Agregar
        await self.participante_repo.agregar(conversacion_id, nuevo_participante)
        
        # Touch para actualizar ultima_actividad
        await self.conversacion_repo.touch(conversacion_id)
