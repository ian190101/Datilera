# app/kernel/domain/acceso/codigo_acceso_uso_entidad.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, AwareDatetime


class CodigoAccesoUso(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None)
    codigo_id: int = Field(description="ID del Código de Acceso que se está usando.")
    usuario_id: int = Field(description="ID del usuario que consumió el código.")
    rol_id: int = Field(description="ID del rol asignado en este uso.")
    consumido_en: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
