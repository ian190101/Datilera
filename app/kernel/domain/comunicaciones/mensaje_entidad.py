# app/kernel/domain/comunicaciones/mensaje_entidad.py

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TipoMensaje(str, Enum):
    """Tipos de mensaje."""
    TEXTO = "texto"
    SISTEMA = "sistema"


class Mensaje(BaseModel):
    """Entidad **Mensaje**.

    - **US-COM-002**: Envío de mensajes con contenido obligatorio (≤4000).
    - **Chat**: *Inmutabilidad de mensajes* (no se editan ni se eliminan),
      con adjuntos gestionados por la entidad `MensajeAdjunto`.
    - **US-COM-003**: La marcación de lectura se resuelve a nivel de repos/lecturas
      (tabla de vistas por usuario), no dentro de esta entidad.
    """

    id: int
    conversacion_id: int
    remitente_id: int
    contenido: str
    tipo: TipoMensaje = TipoMensaje.TEXTO
    reply_a_id: Optional[int] = None
    metadatos: Optional[Dict] = None
    enviado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )

    @field_validator("contenido")
    @classmethod
    def _contenido_valido(cls, v: str) -> str:
        """Valida contenido obligatorio (US-COM-002)."""
        cont = (v or "").strip()
        if not cont:
            raise ValueError("El contenido no puede estar vacío (US-COM-002).")
        if len(cont) > 40000:
            raise ValueError(
                "El contenido no puede exceder 40000 caracteres (US-COM-002)."
            )
        return cont

    # --- Políticas de inmutabilidad del chat ---
    def editar(self, *_args, **_kwargs) -> None:  # pragma: no cover
        """Los mensajes son inmutables."""
        raise ValueError("Los mensajes son inmutables (chat).")

    def eliminar(self, *_args, **_kwargs) -> None:  # pragma: no cover
        """Los mensajes son inmutables."""
        raise ValueError("Los mensajes son inmutables (chat).")
