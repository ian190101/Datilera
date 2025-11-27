# app/kernel/application/comunicaciones/notificaciones/marcar_notificacion_leida.py

from app.kernel.domain.comunicaciones import (
    NotificacionRepositoryPort,
    NotificacionNoEncontrada,
)


class MarcarNotificacionLeidaUseCase:
    """Caso de uso: Marcar notificación como leída (US-COM-008).
    
    Reglas:
    - Solo el usuario destinatario puede marcar
    - Idempotente (no falla si ya está leída)
    """

    def __init__(self, notificacion_repo: NotificacionRepositoryPort):
        self.notificacion_repo = notificacion_repo

    async def ejecutar(
        self,
        notificacion_id: int,
        usuario_id: int,
    ) -> None:
        """Marca una notificación como leída.
        
        Args:
            notificacion_id: ID de la notificación
            usuario_id: Usuario que marca
            
        Raises:
            NotificacionNoEncontrada: Si no existe o no pertenece al usuario
        """
        # Obtener notificación
        notificacion = await self.notificacion_repo.obtener_por_id(notificacion_id)
        
        if not notificacion or notificacion.usuario_id != usuario_id:
            raise NotificacionNoEncontrada(notificacion_id)

        # Si ya está leída, retornar (idempotencia)
        if notificacion.esta_leida():
            return

        # Marcar como leída
        await self.notificacion_repo.marcar_leida(notificacion_id)
