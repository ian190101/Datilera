# app/kernel/domain/seguridad/rol_permiso_entidad.py
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class RolPermiso(BaseModel):
    """
    Entidad de dominio que representa la asignación de un permiso a un rol.
    
    Atributos:
        id: Identificador único de la asignación
        rol_id: ID del rol
        permiso_id: ID del permiso asignado
        asignado_en: Timestamp de cuándo se hizo la asignación
    """
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    id: int
    rol_id: int = Field(..., gt=0)
    permiso_id: int = Field(..., gt=0)
    asignado_en: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def crear(cls, rol_id: int, permiso_id: int) -> RolPermiso:
        """Método de fabrica para crear una nueva asignacion."""
        return cls(
            id=0, 
            rol_id=rol_id,
            permiso_id=permiso_id,
            asignado_en=datetime.now()
        )
