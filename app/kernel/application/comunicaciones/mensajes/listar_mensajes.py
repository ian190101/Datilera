# app/kernel/application/comunicaciones/mensajes/listar_mensajes.py

from typing import List
from app.kernel.domain.comunicaciones import (
    Mensaje,
    ConversacionRepositoryPort,
    ParticipanteRepositoryPort,
    MensajeRepositoryPort,
    ConversacionNoEncontrada,
    ParticipanteNoAutorizado,
)


class ListarMensajesUseCase:
    """Caso de uso: Listar mensajes de conversación.
    
    Reglas:
    - Ordenados por enviado_en ASC
    - Solo participantes pueden ver
    - Paginación
    """

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
        limite: int = 50,
        offset: int = 0,
    ) -> List[Mensaje]:
        """Lista mensajes de una conversación.
        
        Args:
            conversacion_id: ID de la conversación
            usuario_id: Usuario que solicita
            limite: Máximo resultados
            offset: Saltar registros
            
        Returns:
            Lista de mensajes
            
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

        # Listar mensajes
        return await self.mensaje_repo.listar_por_conversacion(
            conversacion_id=conversacion_id,
            limite=limite,
            offset=offset,
        )
