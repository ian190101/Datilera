# app/kernel/application/comunicaciones/notificaciones/crear_notificacion.py

from typing import Dict, Optional
from datetime import datetime

from app.kernel.domain.comunicaciones import (
    Notificacion,
    CanalNotificacion,
    PrioridadNotificacion,
    NotificacionRepositoryPort,
    NotificadorServicePort,
)

# NUEVO: helper para WS
from app.infrastructure.notificaciones.service import publicar_notificacion_nueva


class CrearNotificacionUseCase:
    """Caso de uso: Crear notificación (US-COM-004).
    Reglas:
    - Título y cuerpo obligatorios
    - Persistente (no se elimina)
    - Envío inmediato o programado
    - Soporta múltiples canales
    """

    def __init__(
        self,
        notificacion_repo: NotificacionRepositoryPort,
        notificador_service: NotificadorServicePort,
    ):
        self.notificacion_repo = notificacion_repo
        self.notificador_service = notificador_service

    async def ejecutar(
        self,
        usuario_id: int,
        titulo: str,
        cuerpo: str,
        tipo: str,
        relacionado_tipo: Optional[str] = None,
        relacionado_id: Optional[int] = None,
        canal: CanalNotificacion = CanalNotificacion.IN_APP,
        prioridad: str = "media",
        programada_para: Optional[datetime] = None,
        metadatos: Optional[Dict] = None,
    ) -> Notificacion:
        """Crea una notificación."""
        # Crear notificación (validaciones en entidad)
        notificacion = await self.notificacion_repo.crear(
            usuario_id=usuario_id,
            titulo=titulo,
            cuerpo=cuerpo,
            tipo=tipo,
            relacionado_tipo=relacionado_tipo,
            relacionado_id=relacionado_id,
            canal=canal,
            prioridad=prioridad,
            programada_para=programada_para,
            metadatos=metadatos,
        )

        # Si no está programada, enviar inmediatamente
        if not programada_para:
            await self._enviar_notificacion(notificacion)

        # NUEVO: disparo WebSocket solo para IN_APP no programadas
        if canal == CanalNotificacion.IN_APP and not programada_para:
            await publicar_notificacion_nueva(
                usuario_ids_destino=[notificacion.usuario_id],
                notificacion_id=notificacion.id,
                titulo=notificacion.titulo,
                mensaje=notificacion.cuerpo,
                tipo=notificacion.tipo,
                creado_en=notificacion.creado_en.isoformat(),
                sede_id=notificacion.sede_id,
            )

        return notificacion

    async def _enviar_notificacion(self, notificacion: Notificacion) -> None:
        """Envía notificación según canal configurado."""
        try:
            enviada = False

            if notificacion.canal == CanalNotificacion.IN_APP:
                enviada = await self.notificador_service.enviar_in_app(notificacion)
            elif notificacion.canal == CanalNotificacion.EMAIL:
                enviada = await self.notificador_service.enviar_email(
                    notificacion,
                    destinatario_email="usuario@example.com",  # TODO: obtener del repo
                )
            elif notificacion.canal == CanalNotificacion.PUSH:
                enviada = await self.notificador_service.enviar_push(
                    notificacion,
                    dispositivo_token="device_token",  # TODO: obtener del repo
                )
            elif notificacion.canal == CanalNotificacion.SMS:
                enviada = await self.notificador_service.enviar_sms(
                    notificacion,
                    numero_telefono="+591XXXXXXXX",  # TODO: obtener del repo
                )

            if enviada:
                notificacion.marcar_enviado()
            else:
                notificacion.marcar_fallido("Error en el servicio de notificación")

            await self.notificacion_repo.guardar(notificacion)

        except Exception as e:
            notificacion.marcar_fallido(str(e))
            await self.notificacion_repo.guardar(notificacion)
