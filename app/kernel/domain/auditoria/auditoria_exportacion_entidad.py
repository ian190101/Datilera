# app/kernel/domain/auditoria/auditoria_exportacion_entidad.py

"""
Entidad de Dominio: AuditoriaExportacion
Representa una exportación de datos.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuditoriaExportacion(BaseModel):
    """
    Entidad de dominio para auditoría de exportaciones.
    """
    id: int = 0
    usuario_id: Optional[int] = None
    sede_id: Optional[int] = None
    
    # Tipo de exportación
    tipo: str = Field(..., min_length=1, max_length=50)
    
    # Formato
    formato: str = Field(..., min_length=1, max_length=20)
    
    # Filtros aplicados
    filtros: Optional[Dict[str, Any]] = None
    
    # Cantidad de registros
    total_registros: int = Field(default=0, ge=0)
    
    # Columnas incluidas
    columnas: Optional[List[str]] = None
    
    # Ruta del archivo
    ruta_archivo: Optional[str] = Field(None, max_length=500)
    
    # Estado
    exitoso: bool = True
    mensaje_error: Optional[str] = None
    
    # Timestamps
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    descargado_en: Optional[datetime] = None
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
        frozen=False,
    )
    
    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        """Valida que el tipo de exportación sea válido."""
        tipos_validos = {
            "pagos", "alumnos", "inventario", "reportes", "arqueo",
            "asistencias", "mensualidades", "cursos_extra", "profesoras"
        }
        if v.lower() not in tipos_validos:
            raise ValueError(f"Tipo debe ser uno de: {tipos_validos}")
        return v.lower()
    
    @field_validator("formato")
    @classmethod
    def validar_formato(cls, v: str) -> str:
        """Valida que el formato sea válido."""
        formatos_validos = {"excel", "pdf", "csv"}
        if v.lower() not in formatos_validos:
            raise ValueError(f"Formato debe ser uno de: {formatos_validos}")
        return v.lower()
    
    def marcar_como_descargado(self) -> None:
        """Marca la exportación como descargada."""
        self.descargado_en = datetime.utcnow()
    
    def fue_descargada(self) -> bool:
        """Verifica si la exportación fue descargada."""
        return self.descargado_en is not None
    
    def es_masiva(self, umbral: int = 1000) -> bool:
        """Verifica si es una exportación masiva."""
        return self.total_registros >= umbral
