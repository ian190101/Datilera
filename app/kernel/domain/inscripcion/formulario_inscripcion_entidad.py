# app/kernel/domain/inscripcion/formulario_inscripcion_entidad.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EstadoFormulario(str, Enum):
    BORRADOR = "borrador"
    ENVIADO = "enviado"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


class FormularioInscripcion(BaseModel):
    id: int
    alumno_id: int
    sede_id: int
    gestion: int
    estado: EstadoFormulario = EstadoFormulario.BORRADOR
    observaciones: Optional[str] = None

    turno_id: Optional[int] = None
    revisado_por: Optional[int] = None
    revisado_en: Optional[datetime] = None
    aprobado_por: Optional[int] = None
    aprobado_en: Optional[datetime] = None

    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )

    @field_validator("gestion")
    @classmethod
    def _gestion_valida(cls, v: int) -> int:
        if v < 2000:
            raise ValueError("Gestión inválida")
        return v

    def enviar(self) -> None:
        if self.estado != EstadoFormulario.BORRADOR:
            raise ValueError("Solo un formulario en borrador puede enviarse")
        self.estado = EstadoFormulario.ENVIADO
        self.actualizado_en = datetime.utcnow()

    def marcar_revisado(self, usuario_id: int) -> None:
        self.revisado_por = usuario_id
        self.revisado_en = datetime.utcnow()
        self.actualizado_en = self.revisado_en

    def marcar_aprobado(self, usuario_id: int) -> None:
        if self.estado not in (EstadoFormulario.ENVIADO, EstadoFormulario.RECHAZADO):
            raise ValueError("Para aprobar, el formulario debe estar enviado o rechazado")
        self.aprobado_por = usuario_id
        self.aprobado_en = datetime.utcnow()
        self.estado = EstadoFormulario.APROBADO
        self.actualizado_en = self.aprobado_en

    def rechazar(self, observaciones: Optional[str]) -> None:
        if self.estado != EstadoFormulario.ENVIADO:
            raise ValueError("Para rechazar, el formulario debe estar enviado")
        self.observaciones = (observaciones or "").strip() or None
        self.estado = EstadoFormulario.RECHAZADO
        self.actualizado_en = datetime.utcnow()

    def fijar_turno(self, turno_id: int) -> None:
        if turno_id <= 0:
            raise ValueError("turno_id inválido")
        self.turno_id = turno_id
        self.actualizado_en = datetime.utcnow()
