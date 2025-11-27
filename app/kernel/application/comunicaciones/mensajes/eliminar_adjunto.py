# app/kernel/application/comunicaciones/mensajes/eliminar_adjunto.py

from app.kernel.domain.comunicaciones import (
    MensajeRepositoryPort,
    ParticipanteRepositoryPort,
    MensajeAdjuntoRepositoryPort,
    ArchivoStorageServicePort,
    AdjuntoNoEncontrado,
    ParticipanteNoAutorizado,
)


class EliminarAdjuntoUseCase:
    """Caso de uso: Eliminar adjunto de mensaje.
    
    Reglas:
    - Solo participantes pueden eliminar
    - Elimina del storage externo
    """

    def __init__(
        self,
        mensaje_repo: MensajeRepositoryPort,
        participante_repo: ParticipanteRepositoryPort,
        adjunto_repo: MensajeAdjuntoRepositoryPort,
        storage_service: ArchivoStorageServicePort,
    ):
        self.mensaje_repo = mensaje_repo
        self.participante_repo = participante_repo
        self.adjunto_repo = adjunto_repo
        self.storage_service = storage_service

    async def ejecutar(
        self,
        adjunto_id: int,
        usuario_id: int,
    ) -> bool:
        """Elimina un adjunto.
        
        Args:
            adjunto_id: ID del adjunto
            usuario_id: Usuario que elimina
            
        Returns:
            True si se eliminó
            
        Raises:
            AdjuntoNoEncontrado: Si no existe
            ParticipanteNoAutorizado: Si no es participante
        """
        # Verificar adjunto existe
        adjunto = await self.adjunto_repo.obtener_por_id(adjunto_id)
        if not adjunto:
            raise AdjuntoNoEncontrado(adjunto_id)

        # Obtener mensaje para verificar conversación
        mensaje = await self.mensaje_repo.obtener_por_id(adjunto.mensaje_id)
        if not mensaje:
            raise AdjuntoNoEncontrado(adjunto_id)

        # Verificar que es participante
        es_participante = await self.participante_repo.es_participante(
            mensaje.conversacion_id, usuario_id
        )
        if not es_participante:
            raise ParticipanteNoAutorizado(usuario_id, mensaje.conversacion_id)

        # Eliminar del storage
        await self.storage_service.eliminar_adjunto(adjunto.url)

        # Eliminar registro
        return await self.adjunto_repo.eliminar(adjunto_id)
