# app/kernel/application/comunicaciones/notificaciones/marcar_notificacion_leida_badge.py

from app.infrastructure.db.uow import UnitOfWork # o el puerto UoW que uses
from app.kernel.application.comunicaciones.notificaciones.marcar_notificacion_leida import (
    MarcarNotificacionLeidaUseCase,
)
from app.infrastructure.db.repositories.comunicaciones.notificaciones_repo import (
    NotificacionesRepository,
)
from app.infrastructure.ws.manager import ws_manager


class MarcarNotificacionLeidaConBadgeService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def ejecutar(self, notificacion_id: int, usuario_id: int, sede_id: int) -> None:
        async with self.uow:
            repo = NotificacionesRepository(self.uow.session_required)
            usecase = MarcarNotificacionLeidaUseCase(repo)

            await usecase.ejecutar(notificacion_id=notificacion_id, usuario_id=usuario_id)
            total = await repo.contar_no_leidas(usuario_id=usuario_id, sede_id=sede_id)

        await ws_manager.send_notif_badge(
            usuario_id=usuario_id,
            sede_id=sede_id,
            total_no_leidas=total,
        )