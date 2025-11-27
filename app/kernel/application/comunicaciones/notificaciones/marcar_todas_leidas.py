# app/kernel/application/comunicaciones/notificaciones/marcar_todas_leidas.py

from app.kernel.domain.comunicaciones import NotificacionRepositoryPort


class MarcarTodasLeidasUseCase:
    """Caso de uso: Marcar todas las notificaciones como leídas (US-COM-008)."""

    def __init__(self, notificacion_repo: NotificacionRepositoryPort):
        self.notificacion_repo = notificacion_repo

    async def ejecutar(self, usuario_id: int) -> int:
        """Marca todas las notificaciones del usuario como leídas.
        
        Args:
            usuario_id: Usuario que marca todas
            
        Returns:
            Cantidad de notificaciones marcadas
        """
        return await self.notificacion_repo.marcar_todas_leidas(usuario_id)
