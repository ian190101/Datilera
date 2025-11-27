# app/kernel/application/seguridad/roles/crear_rol.py
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from typing import Optional

from app.kernel.domain.seguridad.rol_entidad import Rol
from app.kernel.domain.seguridad.errors import RolNombreDuplicado
from app.kernel.domain.seguridad.ports import AbstractRolRepository


class CrearRolDTO(BaseModel):
    nombre: str = Field(..., max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)
    activo: bool = True

    @field_validator("nombre")
    @classmethod
    def _norm_nombre(cls, v: str) -> str:
        nv = v.strip()
        if not nv:
            raise ValueError("El nombre del rol no puede estar vacío")
        return nv.upper()


class CrearRol:
    """Caso de uso: Crear un rol con nombre único."""
    def __init__(self, rol_repo: AbstractRolRepository):
        self.rol_repo = rol_repo

    async def execute(self, dto: CrearRolDTO) -> Rol:
        existente = await self.rol_repo.get_by_nombre(dto.nombre)
        if existente:
            raise RolNombreDuplicado(f"Ya existe un rol con nombre '{dto.nombre}'")
        rol = await self.rol_repo.crear(
            nombre=dto.nombre,
            descripcion=dto.descripcion,
            activo=dto.activo,
        )
        return rol
