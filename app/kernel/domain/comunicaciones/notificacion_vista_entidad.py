# app/kernel/domain/comunicaciones/notificacion_vista_entidad.py

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NotificacionVista(BaseModel):
    """Entidad **NotificacionVista**.

    Registra cuando un usuario ve/interactúa con una notificación.
    Útil para analytics y tracking de engagement.
    """

    id: int
    notificacion_id: int
    usuario_id: int
    visto_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
        frozen=True,  # Inmutable una vez creada
    )
