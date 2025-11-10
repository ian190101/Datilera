from __future__ import annotations
from datetime import datetime
from typing import Optional


class NotificacionVista:
    """Entidad **NotificacionVista** (US-COM-008).

    Registra la primera vista de una notificación para métricas.
    """

    def __init__(
        self,
        id: int,
        notificacion_id: int,
        usuario_id: int,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        visto_en: Optional[datetime] = None,
    ):
        self.id = id
        self.notificacion_id = notificacion_id
        self.usuario_id = usuario_id
        self.ip = ip
        self.user_agent = user_agent
        self.visto_en = visto_en or datetime.utcnow()