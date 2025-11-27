# app/kernel/domain/comunicaciones/mensaje_adjunto_entidad.py

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TipoAdjunto(str, Enum):
    """Tipos de adjunto soportados."""
    IMAGEN = "imagen"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENTO = "documento"


class MensajeAdjunto(BaseModel):
    """Entidad **MensajeAdjunto**.

    Gestiona archivos adjuntos a mensajes del chat.
    """

    id: int
    mensaje_id: int
    tipo: TipoAdjunto
    url: str
    nombre_archivo: Optional[str] = None
    tamano_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )

    @field_validator("url")
    @classmethod
    def _url_valida(cls, v: str) -> str:
        """Valida URL obligatoria."""
        url_limpia = (v or "").strip()
        if not url_limpia:
            raise ValueError("La URL del adjunto es obligatoria.")
        if len(url_limpia) > 255:
            raise ValueError("La URL no puede superar 255 caracteres.")
        return url_limpia

    @field_validator("nombre_archivo")
    @classmethod
    def _nombre_valido(cls, v: Optional[str]) -> Optional[str]:
        """Valida longitud del nombre de archivo."""
        if v and len(v) > 160:
            raise ValueError("El nombre de archivo no puede superar 160 caracteres.")
        return v

    def validar_tamano(self, tamano_maximo_bytes: int = 15 * 1024 * 1024) -> None:
        """Valida el tamaño del archivo (por defecto 15MB)."""
        if self.tamano_bytes and self.tamano_bytes > tamano_maximo_bytes:
            raise ValueError(
                f"El archivo excede el tamaño máximo permitido ({tamano_maximo_bytes} bytes)"
            )
