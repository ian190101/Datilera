# app/domain/entities/alumnos/permiso_personal_entidad.py

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import date, datetime


class PermisoPersonalEntidad(BaseModel):
    """Entidad de dominio para permisos del personal"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    id: Optional[int] = None
    personal_id: int
    sede_id: int
    
    # Información del permiso
    fecha_inicio: date
    fecha_fin: date
    tipo_permiso: str  # enfermedad, personal, vacaciones, licencia_medica, etc.
    motivo: str
    
    # Aprobación
    estado: str = "pendiente"  # pendiente, aprobado, rechazado
    aprobado_por_id: Optional[int] = None
    fecha_aprobacion: Optional[datetime] = None
    
    # Auditoría
    creado_en: Optional[datetime] = None

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        estados_validos = ['pendiente', 'aprobado', 'rechazado']
        if v not in estados_validos:
            raise ValueError(f"Estado debe ser uno de: {', '.join(estados_validos)}")
        return v

    @field_validator('tipo_permiso')
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        tipos_validos = ['enfermedad', 'personal', 'vacaciones', 'licencia_medica', 'otro']
        if v not in tipos_validos:
            raise ValueError(f"Tipo de permiso debe ser uno de: {', '.join(tipos_validos)}")
        return v

    def validar_fechas(self) -> bool:
        """Valida que la fecha de fin sea posterior a la de inicio"""
        return self.fecha_fin >= self.fecha_inicio

    @property
    def dias_solicitados(self) -> int:
        """Calcula la cantidad de días del permiso"""
        return (self.fecha_fin - self.fecha_inicio).days + 1
