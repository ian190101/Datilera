# app/kernel/application/seguridad/rol_permiso/revocar_permiso_rol.py
from __future__ import annotations

from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.errors import RolPermisoNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractRolPermisoRepository


class RevocarPermisoRolDTO(BaseModel):
    rol_id: int = Field(..., gt=0)
    permiso_id: int = Field(..., gt=0)


class RevocarPermisoRol:
    """Caso de uso: Revocar un permiso de un rol."""

    def __init__(self, rol_permiso_repo: AbstractRolPermisoRepository):
        self.rol_permiso_repo = rol_permiso_repo

    async def execute(self, dto: RevocarPermisoRolDTO) -> None:
        ok = await self.rol_permiso_repo.revocar(dto.rol_id, dto.permiso_id)
        if not ok:
            raise RolPermisoNoEncontrado(
                f"No se encontró asignación del permiso {dto.permiso_id} al rol {dto.rol_id}"
            )
