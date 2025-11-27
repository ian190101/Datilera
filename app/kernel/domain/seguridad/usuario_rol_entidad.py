# app/kernel/domain/seguridad/usuario_rol_entidad.py
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class UsuarioRol(BaseModel):
    """
    Entidad de dominio que representa la asignación de un rol a un usuario.
    
    Atributos:
        id: Identificador único de la asignación
        usuario_id: ID del usuario
        rol_id: ID del rol asignado
        asignado_en: Timestamp de cuándo se hizo la asignación
    """
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    
    id: int
    usuario_id: int = Field(..., gt=0)
    rol_id: int = Field(..., gt=0)
    asignado_en: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def crear(cls, usuario_id: int, rol_id: int) -> UsuarioRol:
        """Método de fábrica para crear una nueva asignación."""
        return cls(
            id=0,  # Se asignará al persistir
            usuario_id=usuario_id,
            rol_id=rol_id,
            asignado_en=datetime.now()
        )
