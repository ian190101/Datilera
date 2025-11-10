# app/kernel/domain/seguridad/permiso_entidad.py
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict, computed_field


class Accion(str, Enum):
    VER = "VER"
    CREAR = "CREAR"
    EDITAR = "EDITAR"
    ELIMINAR = "ELIMINAR"
    EXPORTAR = "EXPORTAR"
    VER_SENSIBLE = "VER_SENSIBLE"


class Permiso(BaseModel):
    model_config = ConfigDict(use_enum_values=True, frozen=True)

    recurso: str
    accion: Accion

    @computed_field  # type: ignore[misc]
    def nombre_completo(self) -> str:
        return f"{self.recurso}:{self.accion}"
