# app/kernel/application/comunicaciones/notificaciones/contar_no_leidas.py

from app.kernel.domain.comunicaciones import NotificacionRepositoryPort


class ContarNoLeidasUseCase:
    """Caso de uso: Contar notificaciones no leídas (US-COM-008).
    
    Para mostrar el badge/contador en la campanita.
    """

    def __init__(self, notificacion_repo: NotificacionRepositoryPort):
        self.notificacion_repo = notificacion_repo

    async def ejecutar(self, usuario_id: int) -> int:
        """Cuenta notificaciones no leídas del usuario.
        
        Args:
            usuario_id: Usuario que consulta
            
        Returns:
            Cantidad de notificaciones no leídas
        """
        return await self.notificacion_repo.contar_no_leidas(usuario_id)
