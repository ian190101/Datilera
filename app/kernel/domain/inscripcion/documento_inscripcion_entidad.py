# app/kernel/domain/inscripcion/documento_inscripcion_entidad.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EstadoProcesamientoDocumento(str, Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    MARCADO = "marcado"
    ERROR = "error"


class DocumentoInscripcion(BaseModel):
    id: int
    formulario_id: int
    tipo_documento: str
    url: str
    nombre_archivo: str

    mime: Optional[str] = None
    hash_archivo: Optional[str] = Field(default=None, max_length=64)
    tamano_bytes: Optional[int] = None

    estado_procesamiento: EstadoProcesamientoDocumento = EstadoProcesamientoDocumento.PENDIENTE
    procesado_en: Optional[datetime] = None
    intentos: int = 0
    error_ultima: Optional[str] = None
    watermark_url: Optional[str] = None

    creado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )

    @field_validator("tipo_documento", "url", "nombre_archivo")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not (v or "").strip():
            raise ValueError("Campo obligatorio vacío")
        return v.strip()

    @field_validator("tamano_bytes")
    @classmethod
    def _tamano_valido(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("El tamaño no puede ser negativo")
        return v

    def marcar_procesando(self) -> None:
        self.estado_procesamiento = EstadoProcesamientoDocumento.PROCESANDO

    def marcar_marcado(self, watermark_url: str) -> None:
        if not (watermark_url or "").strip():
            raise ValueError("watermark_url es obligatorio")
        self.estado_procesamiento = EstadoProcesamientoDocumento.MARCADO
        self.watermark_url = watermark_url
        self.procesado_en = datetime.utcnow()

    def marcar_error(self, mensaje: str) -> None:
        self.estado_procesamiento = EstadoProcesamientoDocumento.ERROR
        self.error_ultima = (mensaje or "").strip() or None
        self.intentos += 1
