# app/kernel/domain/comunicaciones/mensaje_lectura_entidad.py

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MensajeLectura(BaseModel):
    """Entidad **MensajeLectura** (US-COM-003).

    Registra cuando un usuario marca/lee un mensaje específico.
    Tabla de relación Many-to-Many entre mensajes y usuarios.
    
    Casos de uso:
    - Marcar mensaje como leído (US-COM-003)
    - Mostrar "visto" en el chat
    - Contadores de mensajes no leídos por conversación
    """

    id: int
    mensaje_id: int
    usuario_id: int
    leido_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
        frozen=True,  # Inmutable una vez creada (no se "des-lee" un mensaje)
    )

    def __hash__(self) -> int:
        """Permite usar en sets para eliminar duplicados."""
        return hash((self.mensaje_id, self.usuario_id))

    def __eq__(self, other: object) -> bool:
        """Igualdad basada en mensaje_id y usuario_id."""
        if not isinstance(other, MensajeLectura):
            return False
        return (
            self.mensaje_id == other.mensaje_id
            and self.usuario_id == other.usuario_id
        )
