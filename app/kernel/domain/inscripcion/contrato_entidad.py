# app/kernel/domain/inscripcion/contrato_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Contrato:
    """
    Contrato emitido tras aprobación del formulario.
    Guarda código único, URL del PDF y fecha de emisión.
    """
    id: int
    formulario_id: int
    codigo_contrato: str
    fecha_emision: date
    pdf_url: str | None = None
    creado_en: datetime = None

    def __post_init__(self):
        if not (self.codigo_contrato or "").strip():
            raise ValueError("El código de contrato es obligatorio.")
        self.creado_en = self.creado_en or datetime.utcnow()