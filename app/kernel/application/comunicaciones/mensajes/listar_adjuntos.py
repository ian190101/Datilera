# app/kernel/application/comunicaciones/mensajes/listar_adjuntos.py

from typing import List
from app.kernel.domain.comunicaciones import (
    MensajeAdjunto,
    MensajeRepositoryPort,
    ParticipanteRepositoryPort,
    MensajeAdjuntoRepositoryPort,
    MensajeNoEncontrado,
    ParticipanteNoAutorizado,
)


class ListarAdjuntosUseCase:
    """Caso de uso: Listar adjuntos de un mensaje."""

    def __init__(
        self,
        mensaje_repo: MensajeRepositoryPort,
        participante_repo: ParticipanteRepositoryPort,
        adjunto_repo: MensajeAdjuntoRepositoryPort,
    ):
        self.mensaje_repo = mensaje_repo
        self.participante_repo = participante_repo
        self.adjunto_repo = adjunto_repo

    async def ejecutar(
        self,
        mensaje_id: int,
        usuario_id: int,
    ) -> List[MensajeAdjunto]:
        """Lista adjuntos de un mensaje.
        
        Args:
            mensaje_id: ID del mensaje
            usuario_id: Usuario que solicita
            
        Returns:
            Lista de adjuntos
            
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

        # Listar adjuntos
        return await self.adjunto_repo.listar_por_mensaje(mensaje_id)
