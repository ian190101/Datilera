# app/domain/entities/alumnos/asistencia_personal_entidad.py

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import date, time, datetime


class AsistenciaPersonalEntidad(BaseModel):
    """Entidad de dominio para asistencia del personal"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    id: Optional[int] = None
    personal_id: int  # referencia a Usuario
    fecha: date
    sede_id: int
    
    # Registro de horarios
    hora_entrada: Optional[time] = None
    hora_salida: Optional[time] = None
    
    # Observaciones
    observaciones: Optional[str] = None
    
    # Auditoría
    creado_en: Optional[datetime] = None

    @field_validator('fecha')
    @classmethod
    def validar_fecha(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("No se puede registrar asistencia de fechas futuras")
        return v

    def asistio(self) -> bool:
        """Verifica si el personal asistió"""
        return self.hora_entrada is not None
