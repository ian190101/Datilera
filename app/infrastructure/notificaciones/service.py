# app/infrastructure/notificaciones/service.py

from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.kernel.domain.notificaciones.notificaciones import (
    AbstractNotificacionesService,
    CrearNotificacionInput,
)

from app.infrastructure.ws.events import (
    WSNotificationNewPayload,
    WSNotificationReadPayload,
    build_notification_new_event,
    build_notification_read_event,
)
from app.infrastructure.ws.manager import ws_manager


class NotificacionesService(AbstractNotificacionesService):
    """
    Implementación concreta del servicio de notificaciones.
    Usa WebSocket como primer canal en esta versión.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def notificar_nuevo_reporte(
        self,
        reporte_id: int,
        tutor_ids: List[int],
    ) -> None:
        """
        Método legacy que se mantiene por compatibilidad con Portafolio.
        Por ahora delega en enviar_notificacion para cada tutor.
        """
        for tutor_id in tutor_ids:
            dummy_input = CrearNotificacionInput(
                usuario_id=tutor_id,
                titulo=f"Nuevo reporte #{reporte_id}",
                mensaje="Tienes un nuevo reporte disponible.",
                data={"reporte_id": reporte_id},
            )
            await self.enviar_notificacion(dummy_input)

    async def enviar_notificacion(
        self,
        input_data: CrearNotificacionInput,
    ) -> None:
        """
        Implementación oficial de envío de notificaciones.

        Por ahora:
        - No dispara email ni WebPush todavía.
        - Publica por WebSocket al usuario destino si está conectado.
        """
        # Si tu dominio ya genera una entidad Notificación y devuelve su ID,
        # aquí podrías recibirla por parámetro; por ahora asumimos que
        # aún no tenemos notificacion_id, así que lo tratamos como evento “liviano”.
        payload = WSNotificationNewPayload(
            notificacion_id=input_data.notificacion_id,  # ajusta según tu DTO
            titulo=input_data.titulo,
            mensaje=input_data.mensaje,
            tipo=input_data.tipo,
            creado_en=input_data.creado_en,
            leida=False,
            sede_id=input_data.sede_id,
        )
        event = build_notification_new_event(payload)
        await ws_manager.send_to_user(user_id=input_data.usuario_id, event=event)


async def publicar_notificacion_nueva(
    usuario_ids_destino: Iterable[int],
    notificacion_id: int,
    titulo: str,
    mensaje: str,
    tipo: str,
    creado_en: str,
    sede_id: int,
) -> None:
    """
    Helper para casos de uso que ya persisten notificaciones en BD
    y quieren notificar a varios usuarios (ej. masivo por sede).
    """
    payload = WSNotificationNewPayload(
        notificacion_id=notificacion_id,
        titulo=titulo,
        mensaje=mensaje,
        tipo=tipo,
        creado_en=creado_en,
        leida=False,
        sede_id=sede_id,
    )
    event = build_notification_new_event(payload)

    for user_id in usuario_ids_destino:
        await ws_manager.send_to_user(user_id=user_id, event=event)


async def publicar_notificacion_leida(
    usuario_id: int,
    notificacion_id: int,
    sede_id: int,
) -> None:
    """
    Helper para cuando un usuario marca como leída una notificación
    y quieres sincronizar otros tabs/dispositivos de ese mismo usuario.
    """
    payload = WSNotificationReadPayload(
        notificacion_id=notificacion_id,
        sede_id=sede_id,
    )
    event = build_notification_read_event(payload)
    await ws_manager.send_to_user(user_id=usuario_id, event=event)
