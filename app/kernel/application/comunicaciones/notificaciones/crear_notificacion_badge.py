from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.db.repositories.comunicaciones.notificaciones_repo import (
    NotificacionesRepository,
)
from app.infrastructure.ws.manager import ws_manager
from app.infrastructure.ws.events import (
    WSNotificationNewPayload,
    build_notification_new_event,
)


class CrearNotificacionConWSService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def ejecutar(
        self,
        *,
        usuario_id: int,
        sede_id: int,
        titulo: str,
        cuerpo: str,
        tipo: str,
        metadata: dict | None = None,
    ) -> int:
        async with self.uow:
            repo = NotificacionesRepository(self.uow.session_required)
            notificacion_id = await repo.crear_notificacion(
                usuario_id=usuario_id,
                sede_id=sede_id,
                titulo=titulo,
                cuerpo=cuerpo,
                tipo=tipo,
                metadata=metadata or {},
            )
            total_no_leidas = await repo.contar_no_leidas(usuario_id, sede_id)
            await self.uow.commit()

        # evento de notificación nueva
        notif_payload = WSNotificationNewPayload(
            notificacion_id=notificacion_id,
            titulo=titulo,
            mensaje=cuerpo,
            tipo=tipo,
            creado_en="",  # o string ISO si lo tienes
            leida=False,
            sede_id=sede_id,
        )
        event_new = build_notification_new_event(notif_payload)
        await ws_manager.send_to_user(usuario_id, event_new)

        # badge actualizado
        await ws_manager.send_notif_badge(
            usuario_id=usuario_id,
            sede_id=sede_id,
            total_no_leidas=total_no_leidas,
        )

        return notificacion_id
