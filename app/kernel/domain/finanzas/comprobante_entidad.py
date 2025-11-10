# app/kernel/domain/finanzas/comprobante_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


MIMES_PERMITIDOS_COMPROBANTE = {
    "image/png", "image/jpeg", "application/pdf"
}


@dataclass
class Comprobante:
    """
    Comprobante digital (imagen/PDF) siempre requerido en pagos.
    Se almacena hash para evitar duplicados.
    """
    id: int
    ruta: str
    mime: str
    hash_archivo: str
    creado_en: datetime = None
    descripcion: Optional[str] = None

    def __post_init__(self):
        if self.mime not in MIMES_PERMITIDOS_COMPROBANTE:
            raise ValueError(f"MIME no permitido para comprobante: {self.mime}")
        if not self.hash_archivo:
            raise ValueError("Se requiere hash del comprobante.")
        self.creado_en = self.creado_en or datetime.utcnow()