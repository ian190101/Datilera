# app/kernel/application/seguridad/rol_permiso/asignar_permiso_rol.py
from __future__ import annotations

from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.errors import (
    RolNoEncontrado,
    PermisoNoEncontrado,
    RolPermisoYaAsignado,
)
from app.kernel.domain.seguridad.ports import (
    AbstractRolRepository,
    AbstractPermisoRepository,
    AbstractRolPermisoRepository,
)


class AsignarPermisoRolDTO(BaseModel):
    rol_id: int = Field(..., gt=0)
    permiso_id: int = Field(..., gt=0)


class AsignarPermisoRol:
    """Caso de uso: Asignar un permiso a un rol."""

    def __init__(
        self,
        rol_repo: AbstractRolRepository,
        permiso_repo: AbstractPermisoRepository,
        rol_permiso_repo: AbstractRolPermisoRepository,
    ):
        self.rol_repo = rol_repo
        self.permiso_repo = permiso_repo
        self.rol_permiso_repo = rol_permiso_repo

    async def execute(self, dto: AsignarPermisoRolDTO) -> None:
        # 1) Validar rol existe
        rol_existe = await self.rol_repo.exists(dto.rol_id)
        if not rol_existe:
            raise RolNoEncontrado(f"Rol con ID {dto.rol_id} no encontrado")

        # 2) Validar permiso existe
        permiso_existe = await self.permiso_repo.exists(dto.permiso_id)
        if not permiso_existe:
            raise PermisoNoEncontrado(f"Permiso con ID {dto.permiso_id} no encontrado")

        # 3) Validar que no esté ya asignado
        ya_tiene = await self.rol_permiso_repo.ya_asignado(dto.rol_id, dto.permiso_id)
        if ya_tiene:
            raise RolPermisoYaAsignado(
                f"El rol {dto.rol_id} ya tiene asignado el permiso {dto.permiso_id}"
            )

        # 4) Asignar
        await self.rol_permiso_repo.asignar(dto.rol_id, dto.permiso_id)
