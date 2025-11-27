# app/kernel/domain/finanzas/comprobante_entidad.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Definimos los tipos permitidos (puedes importarlos desde config si prefieres)
MIMES_PERMITIDOS_COMPROBANTE = {
    "image/png", "image/jpeg", "application/pdf"
}

class Comprobante(BaseModel):
    """
    Comprobante digital (imagen/PDF) siempre requerido en pagos.
    Se almacena hash para evitar duplicados.
    """
    id: int
    ruta: str
    mime: str
    hash_archivo: str
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    descripcion: Optional[str] = None

    @field_validator('mime')
    @classmethod
    def validar_mime(cls, v: str) -> str:
        """Verifica que el archivo sea una imagen o PDF válido"""
        if v not in MIMES_PERMITIDOS_COMPROBANTE:
            raise ValueError(f"MIME no permitido para comprobante: {v}")
        return v

    @field_validator('hash_archivo')
    @classmethod
    def validar_hash(cls, v: str) -> str:
        """Asegura que el hash no llegue vacío"""
        if not v or not v.strip():
            raise ValueError("Se requiere hash del comprobante.")
        return v