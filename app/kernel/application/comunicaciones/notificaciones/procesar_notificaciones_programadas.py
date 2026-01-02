# app/kernel/application/comunicaciones/notificaciones/procesar_notificaciones_programadas.py

from datetime import datetime

from typing import List

from app.kernel.domain.comunicaciones import (
    Notificacion,
    CanalNotificacion,
    NotificacionRepositoryPort,
    NotificadorServicePort,
)

# NUEVO: helper para WebSocket
from app.infrastructure.notificaciones.service import publicar_notificacion_nueva


class ProcesarNotificacionesProgramadasUseCase:
    """Caso de uso: Procesar notificaciones programadas pendientes.

    Este caso de uso es ejecutado por un worker/cron job periódicamente
    para enviar notificaciones que ya cumplieron su fecha programada.
    """

    def __init__(
        self,
        notificacion_repo: NotificacionRepositoryPort,
        notificador_service: NotificadorServicePort,
    ):
        self.notificacion_repo = notificacion_repo
        self.notificador_service = notificador_service

    async def ejecutar(self, limite: int = 100) -> int:
        """Procesa notificaciones programadas pendientes.

        Args:
            limite: Máximo de notificaciones a procesar

        Returns:
            Cantidad de notificaciones enviadas
        """
        ahora = datetime.utcnow()

        # Obtener notificaciones pendientes
        notificaciones = await self.notificacion_repo.obtener_programadas_pendientes(
            hasta=ahora
        )

        # Limitar procesamiento
        notificaciones = notificaciones[:limite]
        enviadas = 0

        for notificacion in notificaciones:
            try:
                exito = await self._enviar_notificacion(notificacion)
                if exito:
                    notificacion.marcar_enviado()
                    enviadas += 1

                    # NUEVO: disparo WebSocket para IN_APP
                    if notificacion.canal == CanalNotificacion.IN_APP:
                        await publicar_notificacion_nueva(
                            usuario_ids_destino=[notificacion.usuario_id],
                            notificacion_id=notificacion.id,
                            titulo=notificacion.titulo,
                            mensaje=notificacion.cuerpo,
                            tipo=notificacion.tipo,
                            creado_en=notificacion.creado_en.isoformat(),
                            sede_id=notificacion.sede_id,
                        )
                else:
                    notificacion.marcar_fallido("Error al enviar")

                await self.notificacion_repo.guardar(notificacion)

            except Exception as e:
                notificacion.marcar_fallido(str(e))
                await self.notificacion_repo.guardar(notificacion)

        return enviadas

    async def _enviar_notificacion(self, notificacion: Notificacion) -> bool:
        """Envía notificación según canal."""
        if notificacion.canal == CanalNotificacion.IN_APP:
            return await self.notificador_service.enviar_in_app(notificacion)

        elif notificacion.canal == CanalNotificacion.EMAIL:
            # TODO: obtener email del usuario
            return await self.notificador_service.enviar_email(
                notificacion,
                destinatario_email="usuario@example.com",
            )

        elif notificacion.canal == CanalNotificacion.PUSH:
            # TODO: obtener device token
            return await self.notificador_service.enviar_push(
                notificacion,
                dispositivo_token="device_token",
            )

        elif notificacion.canal == CanalNotificacion.SMS:
            # TODO: obtener teléfono
            return await self.notificador_service.enviar_sms(
                notificacion,
                numero_telefono="+591XXXXXXXX",
            )

        return False
