# app/kernel/domain/seguridad/permiso_entidad.py
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict, computed_field


class Accion(str, Enum):
    VER = "Ver"
    CREAR = "Crear"
    EDITAR = "Editar"
    ELIMINAR = "Eliminar"
    EXPORTAR = "Exportar"
    VER_SENSIBLE = "Ver_Sensible"


class Permiso(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True, 
        frozen=True, 
        from_attributes=True  # Vital para leer desde SQLAlchemy
    )

    id: int
    vista: str   # <--- CAMBIO IMPORTANTE: Coincide con tu columna de BD
    accion: Accion
    descripcion: str | None = None

    @computed_field  # type: ignore[misc]
    def nombre_completo(self) -> str:
        return f"{self.vista}:{self.accion}"
