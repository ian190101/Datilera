# app/kernel/domain/academico/grupo_entidad.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

class Grupo(BaseModel):
    """
    Entidad de dominio que representa un grupo dentro de una sede.
    
    Los grupos son divisiones dentro de una sede (ej: Grupo A, B, C).
    Cada grupo tiene capacidad y pertenece a una gestión específica.
    
    Atributos:
        id: Identificador único
        sede_id: ID de la sede a la que pertenece
        letra: Letra del grupo (A, B, C, etc.)
        capacidad: Número máximo de alumnos
        gestion: Año de gestión
        activo: Estado del grupo
        creado_en: Fecha de creación
    """
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    sede_id: int = Field(..., gt=0, description="ID de la sede")
    nombre: str = Field(..., max_length=100, description="Nombre del grupo")
    letra: str = Field(..., max_length=10, description="Letra del grupo")
    capacidad: int | None = Field(None, ge=0, description="Capacidad máxima")
    gestion: int = Field(..., ge=2020, le=2100, description="Año de gestión")
    activo: bool = Field(default=True, description="Indica si el grupo está activo")
    creado_en: datetime | None = Field(default=None, description="Fecha de creación")

    @field_validator('letra')
    @classmethod
    def validar_letra(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("La letra del grupo no puede estar vacía")
        return v.strip().upper()

    def desactivar(self) -> None:
        """Desactiva el grupo."""
        self.activo = False

    def activar(self) -> None:
        """Activa el grupo."""
        self.activo = True

    def es_activo(self) -> bool:
        return self.activo

    def __str__(self) -> str:
        return f"Grupo {self.letra} - {self.nombre} (Sede {self.sede_id})"

    def __repr__(self) -> str:
        return f"Grupo(id={self.id}, sede_id={self.sede_id}, letra='{self.letra}', gestion={self.gestion})"
