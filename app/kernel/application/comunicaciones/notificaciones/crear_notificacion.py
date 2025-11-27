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
        """Crea una notificación.
        
        Args:
            usuario_id: Usuario destinatario
            titulo: Título (obligatorio, ≤120 chars)
            cuerpo: Cuerpo (obligatorio)
            tipo: Tipo de notificación ('pago_vencimiento', 'nuevo_mensaje', etc.)
            relacionado_tipo: Tipo de entidad relacionada (opcional)
            relacionado_id: ID de entidad relacionada (opcional)
            canal: Canal de envío (in_app, email, push, sms)
            prioridad: Prioridad (baja, media, alta)
            programada_para: Fecha/hora de envío programado (opcional)
            metadatos: Datos adicionales (opcional)
            
        Returns:
            Notificación creada
            
        Raises:
            TituloInvalido: Si título vacío o excede límite
            CuerpoInvalido: Si cuerpo vacío
            TipoNotificacionInvalido: Si tipo inválido
        """
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

        return notificacion

    async def _enviar_notificacion(self, notificacion: Notificacion) -> None:
        """Envía notificación según canal configurado."""
        try:
            enviada = False
            
            if notificacion.canal == CanalNotificacion.IN_APP:
                enviada = await self.notificador_service.enviar_in_app(notificacion)
            
            elif notificacion.canal == CanalNotificacion.EMAIL:
                # Aquí necesitarías obtener el email del usuario
                # desde un repositorio de usuarios
                enviada = await self.notificador_service.enviar_email(
                    notificacion, 
                    destinatario_email="usuario@example.com"  # TODO: obtener del repo
                )
            
            elif notificacion.canal == CanalNotificacion.PUSH:
                # Necesitarías el token del dispositivo
                enviada = await self.notificador_service.enviar_push(
                    notificacion,
                    dispositivo_token="device_token"  # TODO: obtener del repo
                )
            
            elif notificacion.canal == CanalNotificacion.SMS:
                # Necesitarías el número de teléfono
                enviada = await self.notificador_service.enviar_sms(
                    notificacion,
                    numero_telefono="+591XXXXXXXX"  # TODO: obtener del repo
                )

            if enviada:
                notificacion.marcar_enviado()
            else:
                notificacion.marcar_fallido("Error en el servicio de notificación")
            
            await self.notificacion_repo.guardar(notificacion)

        except Exception as e:
            notificacion.marcar_fallido(str(e))
            await self.notificacion_repo.guardar(notificacion)
