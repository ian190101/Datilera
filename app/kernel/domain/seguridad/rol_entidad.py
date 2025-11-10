# app/kernel/domain/seguridad/rol_entidad.py
from __future__ import annotations

from typing import List, Set
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from .permiso_entidad import Permiso, Accion


class Rol(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    nombre: str
    descripcion: str = ""
    permisos: List[Permiso] = []

    # cache interno (no serializable)
    _permisos_set: Set[str] = set()

    @model_validator(mode="after")
    def _build_cache(self) -> "Rol":
        self._permisos_set = {p.nombre_completo for p in self.permisos}
        return self

    def agregar_permiso(self, permiso: Permiso) -> None:
        if permiso not in self.permisos:
            self.permisos.append(permiso)
            self._permisos_set.add(permiso.nombre_completo)

    def tiene_permiso(self, recurso: str, accion: Accion) -> bool:
        return f"{recurso}:{accion.value}" in self._permisos_set
