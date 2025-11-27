# app/kernel/application/comunicaciones/mensajes/obtener_mensaje.py

from app.kernel.domain.comunicaciones import (
    Mensaje,
    MensajeRepositoryPort,
    ParticipanteRepositoryPort,
    MensajeNoEncontrado,
    ParticipanteNoAutorizado,
)


class ObtenerMensajeUseCase:
    """Caso de uso: Obtener detalle de mensaje.
    
    Reglas:
    - Solo participantes de la conversación pueden ver
    """

    def __init__(
        self,
        mensaje_repo: MensajeRepositoryPort,
        participante_repo: ParticipanteRepositoryPort,
    ):
        self.mensaje_repo = mensaje_repo
        self.participante_repo = participante_repo

    async def ejecutar(
        self,
        mensaje_id: int,
        usuario_id: int,
    ) -> Mensaje:
        """Obtiene un mensaje por ID.
        
        Args:
            mensaje_id: ID del mensaje
            usuario_id: Usuario que solicita
            
        Returns:
            Mensaje encontrado
            
        Raises:
            MensajeNoEncontrado: Si no existe
            ParticipanteNoAutorizado: Si no es participante de la conversación
        """
        # Obtener mensaje
        mensaje = await self.mensaje_repo.obtener_por_id(mensaje_id)
        if not mensaje:
            raise MensajeNoEncontrado(mensaje_id)

        # Verificar que es participante de la conversación
        es_participante = await self.participante_repo.es_participante(
            mensaje.conversacion_id, usuario_id
        )
        if not es_participante:
            raise ParticipanteNoAutorizado(usuario_id, mensaje.conversacion_id)

        return mensaje
