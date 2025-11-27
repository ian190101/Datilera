# app/kernel/application/comunicaciones/notificaciones/obtener_notificacion.py

from app.kernel.domain.comunicaciones import (
    Notificacion,
    NotificacionRepositoryPort,
    NotificacionVistaRepositoryPort,
    NotificacionNoEncontrada,
)


class ObtenerNotificacionUseCase:
    """Caso de uso: Obtener detalle de notificación.
    
    Reglas:
    - Solo el usuario destinatario puede ver
    - Registra vista automáticamente
    """

    def __init__(
        self,
        notificacion_repo: NotificacionRepositoryPort,
        vista_repo: NotificacionVistaRepositoryPort,
    ):
        self.notificacion_repo = notificacion_repo
        self.vista_repo = vista_repo

    async def ejecutar(
        self,
        notificacion_id: int,
        usuario_id: int,
    ) -> Notificacion:
        """Obtiene una notificación por ID.
        
        Args:
            notificacion_id: ID de la notificación
            usuario_id: Usuario que solicita
            
        Returns:
            Notificación encontrada
            
        Raises:
            NotificacionNoEncontrada: Si no existe o no pertenece al usuario
        """
        # Obtener notificación
        notificacion = await self.notificacion_repo.obtener_por_id(notificacion_id)
        
        if not notificacion or notificacion.usuario_id != usuario_id:
            raise NotificacionNoEncontrada(notificacion_id)

        # Registrar vista (si no estaba vista)
        ya_vista = await self.vista_repo.ya_vista(notificacion_id, usuario_id)
        if not ya_vista:
            await self.vista_repo.registrar_vista(notificacion_id, usuario_id)

        return notificacion
