# app/domain/entities/alumnos/tutor_entidad.py

from pydantic import BaseModel, ConfigDict, field_validator, EmailStr, Field
from typing import Optional
from datetime import datetime


class TutorEntidad(BaseModel):
    """Entidad de dominio para Tutor"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    id: Optional[int] = None
    
    # Información personal
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    tipo_documento: str = "CI"
    numero_documento: str
    
    # Contacto
    telefono_principal: str
    telefono_alternativo: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    
    # Laborales
    ocupacion: Optional[str] = None
    lugar_trabajo: Optional[str] = None
    telefono_trabajo: Optional[str] = None
    
    # Estado
    activo: bool = True
    
    # Auditoría
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    @field_validator('telefono_principal', 'telefono_alternativo', 'telefono_trabajo')
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v.strip()) < 7:
            raise ValueError("El teléfono debe tener al menos 7 dígitos")
        return v.strip() if v else None

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del tutor"""
        if self.apellido_materno:
            return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"
        return f"{self.nombres} {self.apellido_paterno}"
