from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Dict


class CanalNotificacion(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"


class Prioridad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class NotificacionInmutableError(Exception):
    """Las notificaciones son persistentes y no se eliminan."""


class Notificacion:
    """Entidad **Notificacion** (US-COM-004, US-COM-008).

    Reglas clave del documento:
    - Persistentes y **no borrables** (campanita).
    - Agrupación por `tipo` y posibilidad de marcar como leídas.
    - Canales soportados mediante adaptadores (puerto Notificador fuera del dominio).
    """

    def __init__(
        self,
        id: int,
        usuario_id: int,
        titulo: str,
        cuerpo: str,
        tipo: str,
        relacionado_tipo: Optional[str] = None,
        relacionado_id: Optional[int] = None,
        prioridad: Prioridad = Prioridad.MEDIA,
        programada_para: Optional[datetime] = None,
        enviado_en: Optional[datetime] = None,
        leido_en: Optional[datetime] = None,
        metadatos: Optional[Dict] = None,
    ):
        t = (titulo or "").strip()
        if not t:
            raise ValueError("El título no puede estar vacío (US-COM-004).")
        if len(t) > 120:
            raise ValueError("El título no puede superar 120 caracteres (US-COM-004).")
        c = (cuerpo or "").strip()
        if not c:
            raise ValueError("El cuerpo no puede estar vacío (US-COM-004).")

        self.id = id
        self.usuario_id = usuario_id
        self.titulo = t
        self.cuerpo = c
        self.tipo = tipo
        self.relacionado_tipo = relacionado_tipo
        self.relacionado_id = relacionado_id
        self.prioridad = prioridad
        self.programada_para = programada_para
        self.enviado_en = enviado_en
        self.leido_en = leido_en
        self.metadatos = metadatos or {}

    # Persistencia/inmutabilidad
    def eliminar(self) -> None:  # pragma: no cover
        raise NotificacionInmutableError("Las notificaciones son persistentes y no se eliminan.")

    def marcar_leido(self) -> None:
        """Marca como leída (US-COM-008)."""
        self.leido_en = datetime.utcnow()