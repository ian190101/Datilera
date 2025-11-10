# app/kernel/domain/inscripcion/firma_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Firma:
    """
    Firma digital asociada al formulario (padre/madre/tutor).
    Se guarda la URL de la imagen generada desde el canvas con marca temporal.
    """
    id: int
    formulario_id: int
    firmante: str          # ej.: "madre", "padre", "tutor"
    firma_url: str
    firmado_en: datetime = None
    ip_origen: str | None = None
    user_agent: str | None = None

    def __post_init__(self):
        if not (self.firmante or "").strip():
            raise ValueError("El firmante es obligatorio.")
        if not (self.firma_url or "").strip():
            raise ValueError("La URL de la firma es obligatoria.")
        self.firmado_en = self.firmado_en or datetime.utcnow()