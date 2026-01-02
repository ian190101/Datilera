# app/kernel/application/comunicaciones/notificaciones/marcar_todas_leidas_badge.py

from app.infrastructure.db.uow import UnitOfWork
from app.kernel.application.comunicaciones.notificaciones.marcar_todas_leidas import (
    MarcarTodasLeidasUseCase,
)
from app.infrastructure.db.repositories.comunicaciones.notificaciones_repo import (
    NotificacionesRepository,
)

from app.infrastructure.ws.manager import ws_manager


# marcar_todas_leidas_badge.py

class MarcarTodasLeidasConBadgeService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def ejecutar(self, usuario_id: int, sede_id: int) -> int:
        async with self.uow:
            repo = NotificacionesRepository(self.uow.session_required)
            usecase = MarcarTodasLeidasUseCase(repo)

            count = await usecase.ejecutar(usuario_id=usuario_id)
            total = await repo.contar_no_leidas(usuario_id=usuario_id, sede_id=sede_id)

        await ws_manager.send_notif_badge(
            usuario_id=usuario_id,
            sede_id=sede_id,
            total_no_leidas=total,
        )
        return count

