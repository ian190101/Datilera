from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional


class TipoMensaje(str, Enum):
    TEXTO = "texto"
    SISTEMA = "sistema"


class MensajeInmutableError(Exception):
    """Operación prohibida por política de inmutabilidad del chat."""


class Mensaje:
    """Entidad **Mensaje**.

    - **US-COM-002**: Envío de mensajes con contenido obligatorio (≤4000).
    - **Chat**: *Inmutabilidad de mensajes* (no se editan ni se eliminan),
      con adjuntos gestionados por la entidad `MensajeAdjunto`.
    - **US-COM-003**: La marcación de lectura se resuelve a nivel de repos/lecturas
      (tabla de vistas por usuario), no dentro de esta entidad.
    """

    def __init__(
        self,
        id: int,
        conversacion_id: int,
        remitente_id: int,
        contenido: str,
        tipo: TipoMensaje = TipoMensaje.TEXTO,
        metadatos: Optional[dict] = None,
        creado_en: Optional[datetime] = None,
    ):
        cont = (contenido or "").strip()
        if not cont:
            raise ValueError("El contenido no puede estar vacío (US-COM-002).")
        if len(cont) > 4000:
            raise ValueError("El contenido no puede exceder 4000 caracteres (US-COM-002).")

        self.id = id
        self.conversacion_id = conversacion_id
        self.remitente_id = remitente_id
        self.contenido = cont
        self.tipo = tipo
        self.metadatos = metadatos or {}
        self.creado_en = creado_en or datetime.utcnow()

    # --- Políticas de inmutabilidad del chat ---
    def editar(self, *_args, **_kwargs) -> None:  # pragma: no cover
        raise MensajeInmutableError("Los mensajes son inmutables (chat).")

    def eliminar(self, *_args, **_kwargs) -> None:  # pragma: no cover
        raise MensajeInmutableError("Los mensajes son inmutables (chat).")