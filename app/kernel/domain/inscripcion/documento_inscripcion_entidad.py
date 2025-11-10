# app/kernel/domain/inscripcion/documento_inscripcion_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


MIMES_PERMITIDOS_DOC = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}


@dataclass
class DocumentoInscripcion:
    """
    Documento digital asociado al formulario (certificados, carnets, etc.).

    Reglas:
    - MIME permitido: PDF/PNG/JPEG (más tipos pueden añadirse en políticas/adaptadores).
    - `url` y `nombre_archivo` obligatorios.
    """
    id: int
    formulario_id: int
    tipo_documento: str
    url: str
    nombre_archivo: str
    creado_en: datetime = None
    mime: str | None = None  # opcional a nivel dominio (infra puede completarlo)

    def __post_init__(self):
        if not (self.tipo_documento or "").strip():
            raise ValueError("El tipo de documento es obligatorio.")
        if not (self.url or "").strip():
            raise ValueError("La URL del documento es obligatoria.")
        if not (self.nombre_archivo or "").strip():
            raise ValueError("El nombre de archivo es obligatorio.")
        if self.mime and self.mime not in MIMES_PERMITIDOS_DOC:
            raise ValueError(f"MIME no permitido para documento: {self.mime}")
        self.creado_en = self.creado_en or datetime.utcnow()