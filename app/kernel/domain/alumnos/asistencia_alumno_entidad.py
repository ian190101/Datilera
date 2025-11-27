# app/domain/entities/alumnos/asistencia_alumno_entidad.py

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import date, time, datetime


class AsistenciaAlumnoEntidad(BaseModel):
    """Entidad de dominio para asistencia de alumnos"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    id: Optional[int] = None
    alumno_id: int
    fecha: date
    sede_id: int
    
    # Registro de horarios
    hora_entrada: Optional[time] = None
    hora_salida: Optional[time] = None
    hora_retraso: Optional[time] = None
    
    # Observaciones
    observaciones: Optional[str] = None
    
    # Auditoría
    creado_en: Optional[datetime] = None
    registrado_por_id: Optional[int] = None

    @field_validator('fecha')
    @classmethod
    def validar_fecha(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("No se puede registrar asistencia de fechas futuras")
        return v

    def tiene_retraso(self) -> bool:
        """Verifica si el alumno llegó con retraso"""
        return self.hora_retraso is not None

    def asistio(self) -> bool:
        """Verifica si el alumno asistió"""
        return self.hora_entrada is not None
