# app/kernel/application/seguridad/roles/editar_rol.py
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.kernel.domain.seguridad.rol_entidad import Rol
from app.kernel.domain.seguridad.errors import RolNoEncontrado, RolNombreDuplicado
from app.kernel.domain.seguridad.ports import AbstractRolRepository


class EditarRolDTO(BaseModel):
    rol_id: int = Field(..., gt=0)
    nombre: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)
    activo: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def _norm_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        nv = v.strip()
        if not nv:
            raise ValueError("El nombre del rol no puede estar vacío")
        return nv.upper()


class EditarRol:
    """Caso de uso: Editar un rol existente."""
    def __init__(self, rol_repo: AbstractRolRepository):
        self.rol_repo = rol_repo

    async def execute(self, dto: EditarRolDTO) -> Rol:
        actual = await self.rol_repo.get(dto.rol_id)
        if not actual:
            raise RolNoEncontrado(f"Rol con ID {dto.rol_id} no encontrado")

        if dto.nombre and dto.nombre != actual.nombre:
            colision = await self.rol_repo.get_by_nombre(dto.nombre)
            if colision and getattr(colision, "id", None) != actual.id:
                raise RolNombreDuplicado(f"Ya existe un rol con nombre '{dto.nombre}'")

        data = {k: v for k, v in dto.model_dump().items() if k != "rol_id" and v is not None}
        actualizado = await self.rol_repo.update(dto.rol_id, data)
        return actualizado
