# app/kernel/application/comunicaciones/notificaciones/listar_tipos_notificaciones.py

from typing import List
from app.kernel.domain.comunicaciones import NotificacionRepositoryPort


class ListarTiposNotificacionesUseCase:
    """Caso de uso: Listar tipos de notificaciones disponibles.
    
    Para configuración de preferencias de usuario o administración.
    """

    def __init__(self, notificacion_repo: NotificacionRepositoryPort):
        self.notificacion_repo = notificacion_repo

    async def ejecutar(self) -> List[str]:
        """Lista tipos de notificaciones disponibles en el sistema.
        
        Returns:
            Lista de tipos (ej: ['pago_vencimiento', 'nuevo_mensaje', etc.])
        """
        return await self.notificacion_repo.listar_tipos_disponibles()
