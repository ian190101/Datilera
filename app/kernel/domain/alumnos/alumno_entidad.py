# app/domain/entities/alumnos/alumno_entidad.py

from pydantic import BaseModel, ConfigDict, field_validator, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class AlumnoEntidad(BaseModel):
    """Entidad de dominio para Alumno"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    # Identificación
    id: Optional[int] = None
    sede_id: int
    codigo_alumno: Optional[str] = None
    
    # Información personal
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    fecha_nacimiento: date
    genero: str  # 'M' o 'F'
    tipo_documento: str = "CI"  # CI, Pasaporte, etc.
    numero_documento: str
    
    # Contacto
    foto_url: Optional[str] = None
    
    # Información académica
    turno_id: int
    fecha_ingreso: date
    
    # Estado
    estado: str = "activo"  # activo, inactivo, retirado, egresado
    activo: bool = True
    
    # Auditoría
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None
    creado_por_id: Optional[int] = None

    @field_validator('genero')
    @classmethod
    def validar_genero(cls, v: str) -> str:
        if v not in ['M', 'F']:
            raise ValueError("El género debe ser 'M' o 'F'")
        return v

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        estados_validos = ['activo', 'inactivo', 'retirado', 'egresado']
        if v not in estados_validos:
            raise ValueError(f"Estado debe ser uno de: {', '.join(estados_validos)}")
        return v

    @field_validator('numero_documento')
    @classmethod
    def validar_documento(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("El número de documento es requerido")
        return v.strip()

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del alumno"""
        if self.apellido_materno:
            return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"
        return f"{self.nombres} {self.apellido_paterno}"

    @property
    def edad(self) -> int:
        """Calcula la edad del alumno"""
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad

    def esta_activo(self) -> bool:
        """Verifica si el alumno está activo"""
        return self.activo and self.estado == "activo"
