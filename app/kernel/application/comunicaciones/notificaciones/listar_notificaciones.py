# app/kernel/application/comunicaciones/notificaciones/listar_notificaciones.py

from typing import List, Optional
from app.kernel.domain.comunicaciones import (
    Notificacion,
    NotificacionRepositoryPort,
)


class ListarNotificacionesUseCase:
    """Caso de uso: Listar notificaciones del usuario (US-COM-008).
    
    Reglas:
    - Ordenadas por creado_en DESC
    - Filtros opcionales: tipo, leídas
    - Paginación
    """

    def __init__(self, notificacion_repo: NotificacionRepositoryPort):
        self.notificacion_repo = notificacion_repo

    async def ejecutar(
        self,
        usuario_id: int,
        tipo: Optional[str] = None,
        leidas: Optional[bool] = None,
        limite: int = 20,
        offset: int = 0,
    ) -> List[Notificacion]:
        """Lista notificaciones del usuario.
        
        Args:
            usuario_id: Usuario que solicita
            tipo: Filtrar por tipo (opcional)
            leidas: Filtrar por leídas/no leídas (opcional)
            limite: Máximo resultados
            offset: Saltar registros
            
        Returns:
            Lista de notificaciones
        """
        return await self.notificacion_repo.listar_por_usuario(
            usuario_id=usuario_id,
            tipo=tipo,
            leidas=leidas,
            limite=limite,
            offset=offset,
        )
