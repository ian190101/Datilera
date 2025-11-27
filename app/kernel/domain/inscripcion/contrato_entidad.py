# app/kernel/domain/inscripcion/contrato_entidad.py
from __future__ import annotations
from datetime import date, datetime
from typing import Optional, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Contrato(BaseModel):
    id: int
    formulario_id: int
    sede_id: int
    codigo_contrato: str

    numeracion_sede: Optional[int] = None
    pdf_url: Optional[str] = None
    fecha_emision: date = Field(default_factory=date.today)

    plantilla_version: Optional[int] = None
    variables_json: Optional[Dict[str, object]] = None

    creado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )

    @field_validator("codigo_contrato")
    @classmethod
    def _codigo_obligatorio(cls, v: str) -> str:
        if not (v or "").strip():
            raise ValueError("El código de contrato es obligatorio")
        return v.strip()

    def asignar_numeracion(self, numeracion_sede: int) -> None:
        if numeracion_sede <= 0:
            raise ValueError("La numeración por sede debe ser positiva")
        self.numeracion_sede = numeracion_sede
