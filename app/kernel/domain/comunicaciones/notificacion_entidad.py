# app/kernel/domain/comunicaciones/notificacion_entidad.py

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CanalNotificacion(str, Enum):
    """Canales de notificación soportados."""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class PrioridadNotificacion(str, Enum):
    """Prioridades de notificación."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class EstadoNotificacion(str, Enum):
    """Estados de notificación."""
    PENDIENTE = "pendiente"
    ENVIADA = "enviada"
    FALLIDA = "fallida"


class Notificacion(BaseModel):
    """Entidad **Notificacion** (US-COM-004, US-COM-008).

    Reglas clave del documento:
    - Persistentes y **no borrables** (campanita).
    - Agrupación por `tipo` y posibilidad de marcar como leídas.
    - Canales soportados mediante adaptadores (puerto Notificador fuera del dominio).
    """

    id: int
    usuario_id: int
    titulo: str
    cuerpo: str
    tipo: str  # 'pago_vencimiento', 'nuevo_mensaje', 'alerta_stock', etc.
    relacionado_tipo: Optional[str] = None  # 'pago', 'mensaje', 'actividad'
    relacionado_id: Optional[int] = None
    canal: CanalNotificacion = CanalNotificacion.IN_APP
    prioridad: PrioridadNotificacion = PrioridadNotificacion.MEDIA
    estado: EstadoNotificacion = EstadoNotificacion.PENDIENTE
    programada_para: Optional[datetime] = None
    enviado: bool = False
    enviado_en: Optional[datetime] = None
    leido_en: Optional[datetime] = None
    metadatos: Optional[Dict] = None
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )

    @field_validator("titulo")
    @classmethod
    def _titulo_valido(cls, v: str) -> str:
        """Valida título obligatorio (US-COM-004)."""
        t = (v or "").strip()
        if not t:
            raise ValueError("El título no puede estar vacío (US-COM-004).")
        if len(t) > 120:
            raise ValueError("El título no puede superar 120 caracteres (US-COM-004).")
        return t

    @field_validator("cuerpo")
    @classmethod
    def _cuerpo_valido(cls, v: str) -> str:
        """Valida cuerpo obligatorio (US-COM-004)."""
        c = (v or "").strip()
        if not c:
            raise ValueError("El cuerpo no puede estar vacío (US-COM-004).")
        return c

    @field_validator("tipo")
    @classmethod
    def _tipo_valido(cls, v: str) -> str:
        """Valida tipo obligatorio."""
        t = (v or "").strip()
        if not t:
            raise ValueError("El tipo de notificación es obligatorio.")
        if len(t) > 50:
            raise ValueError("El tipo no puede superar 50 caracteres.")
        return t

    # --- Comportamiento ---
    def marcar_leido(self) -> None:
        """Marca como leída (US-COM-008)."""
        if not self.leido_en:
            self.leido_en = datetime.utcnow()

    def marcar_enviado(self) -> None:
        """Marca como enviada."""
        self.enviado = True
        self.enviado_en = datetime.utcnow()
        self.estado = EstadoNotificacion.ENVIADA

    def marcar_fallido(self, error: Optional[str] = None) -> None:
        """Marca como fallida."""
        self.estado = EstadoNotificacion.FALLIDA
        if error and self.metadatos is None:
            self.metadatos = {}
        if error:
            self.metadatos["error"] = error

    def esta_leida(self) -> bool:
        """Verifica si está leída."""
        return self.leido_en is not None

    def esta_programada(self) -> bool:
        """Verifica si está programada para envío futuro."""
        return self.programada_para is not None and not self.enviado

    # Persistencia/inmutabilidad
    def eliminar(self) -> None:  # pragma: no cover
        """Las notificaciones son inmutables."""
        raise ValueError("Las notificaciones son persistentes y no se eliminan.")
