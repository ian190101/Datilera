from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Políticas específicas del chat (Historias: adjuntos imagen/PDF/Word ≤ 10 MB)
MIMES_PERMITIDOS = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_ADJUNTO_MB = 15


class AdjuntoNoPermitido(Exception):
    """Violación de reglas de adjuntos del chat (≤10MB, tipos permitidos)."""


@dataclass(frozen=True)
class ArchivoAdjunto:
    nombre: str
    mime: str
    tamano_bytes: int
    ruta: Optional[str] = None  # La infraestructura resuelve el storage real
    checksum: Optional[str] = None

    def __post_init__(self):
        if not self.nombre:
            raise AdjuntoNoPermitido("El adjunto debe tener nombre.")
        if self.tamano_bytes <= 0:
            raise AdjuntoNoPermitido("El tamaño del adjunto debe ser positivo.")
        if self.mime not in MIMES_PERMITIDOS:
            raise AdjuntoNoPermitido(f"MIME no permitido para chat: {self.mime}.")
        if self.tamano_bytes > MAX_ADJUNTO_MB * 1024 * 1024:
            raise AdjuntoNoPermitido(f"Adjunto excede {MAX_ADJUNTO_MB} MB.")


class MensajeAdjunto:
    """Entidad **MensajeAdjunto** (US-COM-002).

    Representa un archivo asociado a un mensaje del chat. No se limita la
    cantidad por mensaje en el dominio; los límites operativos pueden
    imponerse en la capa de aplicación/infraestructura.
    """

    def __init__(self, id: int, mensaje_id: int, adjunto: ArchivoAdjunto, creado_en: Optional[datetime] = None):
        self.id = id
        self.mensaje_id = mensaje_id
        self.adjunto = adjunto
        self.creado_en = creado_en or datetime.utcnow()