# app/kernel/domain/inscripcion/formulario_respuesta_entidad.py
from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FormularioRespuesta(BaseModel):
    id: int
    formulario_id: int
    campo: str
    valor: str
    seccion: Optional[str] = Field(default=None, max_length=40)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )

    @field_validator("campo")
    @classmethod
    def _campo_obligatorio(cls, v: str) -> str:
        if not (v or "").strip():
            raise ValueError("El campo es obligatorio")
        return v.strip()
