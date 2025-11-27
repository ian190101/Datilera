# app/kernel/application/comunicaciones/notificaciones/crear_notificacion_programada.py

from typing import Dict, Optional
from datetime import datetime
from app.kernel.domain.comunicaciones import (
    Notificacion,
    CanalNotificacion,
    NotificacionRepositoryPort,
)


class CrearNotificacionProgramadaUseCase:
    """Caso de uso: Crear notificación programada.
    
    Reglas:
    - Se crea pero no se envía
    - Un proceso asíncrono la enviará en la fecha/hora indicada
    """

    def __init__(self, notificacion_repo: NotificacionRepositoryPort):
        self.notificacion_repo = notificacion_repo

    async def ejecutar(
        self,
        usuario_id: int,
        titulo: str,
        cuerpo: str,
        tipo: str,
        programada_para: datetime,
        relacionado_tipo: Optional[str] = None,
        relacionado_id: Optional[int] = None,
        canal: CanalNotificacion = CanalNotificacion.IN_APP,
        prioridad: str = "media",
        metadatos: Optional[Dict] = None,
    ) -> Notificacion:
        """Crea una notificación programada.
        
        Args:
            usuario_id: Usuario destinatario
            titulo: Título
            cuerpo: Cuerpo
            tipo: Tipo de notificación
            programada_para: Fecha/hora de envío
            relacionado_tipo: Tipo relacionado (opcional)
            relacionado_id: ID relacionado (opcional)
            canal: Canal de envío
            prioridad: Prioridad
            metadatos: Datos adicionales
            
        Returns:
            Notificación programada creada
            
        Raises:
            ValueError: Si programada_para es en el pasado
        """
        # Validar que la fecha es futura
        if programada_para <= datetime.utcnow():
            raise ValueError("La fecha programada debe ser futura")

        # Crear notificación programada
        return await self.notificacion_repo.crear(
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
