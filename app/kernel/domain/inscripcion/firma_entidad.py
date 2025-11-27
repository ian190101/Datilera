# app/kernel/domain/inscripcion/firma_entidad.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TipoFirmante(str, Enum):
    MADRE = "madre"
    PADRE = "padre"
    TUTOR = "tutor"


class Firma(BaseModel):
    id: int
    formulario_id: int
    tipo_firmante: TipoFirmante
    firmante: str
    firma_url: str
    firmado_en: datetime = Field(default_factory=datetime.utcnow)
    ip: Optional[str] = Field(default=None, max_length=50)
    user_agent: Optional[str] = None

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )

    @field_validator("firmante", "firma_url")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not (v or "").strip():
            raise ValueError("Campo obligatorio vacío")
        return v.strip()
