# app/domain/entities/alumnos/alumno_hermano_entidad.py

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import date, datetime


class AlumnoHermanoEntidad(BaseModel):
    """Entidad de dominio para hermanos del alumno"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    id: Optional[int] = None
    alumno_id: int
    
    nombres: str
    apellidos: str
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    estudia_en_jardin: bool = False
    lugar_ocupa: int = 1  # Orden entre hermanos (1, 2, 3...)
    
    # Auditoría
    creado_en: Optional[datetime] = None

    @field_validator('genero')
    @classmethod
    def validar_genero(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ['M', 'F']:
            raise ValueError("El género debe ser 'M', 'F' o None")
        return v

    @field_validator('lugar_ocupa')
    @classmethod
    def validar_lugar(cls, v: int) -> int:
        if v < 1:
            raise ValueError("El lugar que ocupa debe ser al menos 1")
        return v

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del hermano"""
        return f"{self.nombres} {self.apellidos}"

    @property
    def edad(self) -> Optional[int]:
        """Calcula la edad del hermano si tiene fecha de nacimiento"""
        if not self.fecha_nacimiento:
            return None
        hoy = date.today()
        edad = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day):
            edad -= 1
        return edad
