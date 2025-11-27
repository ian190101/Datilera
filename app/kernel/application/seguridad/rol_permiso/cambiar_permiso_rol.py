# app/kernel/application/seguridad/rol_permiso/cambiar_permiso_rol.py
from __future__ import annotations

from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.errors import (
    RolNoEncontrado,
    PermisoNoEncontrado,
    RolPermisoNoEncontrado,
    RolPermisoYaAsignado,
)
from app.kernel.domain.seguridad.ports import (
    AbstractRolRepository,
    AbstractPermisoRepository,
    AbstractRolPermisoRepository,
)


class CambiarPermisoRolDTO(BaseModel):
    rol_id: int = Field(..., gt=0)
    permiso_anterior_id: int = Field(..., gt=0)
    permiso_nuevo_id: int = Field(..., gt=0)


class CambiarPermisoRol:
    """Caso de uso: Cambiar permiso asignado a un rol."""

    def __init__(
        self,
        rol_repo: AbstractRolRepository,
        permiso_repo: AbstractPermisoRepository,
        rol_permiso_repo: AbstractRolPermisoRepository,
    ):
        self.rol_repo = rol_repo
        self.permiso_repo = permiso_repo
        self.rol_permiso_repo = rol_permiso_repo

    async def execute(self, dto: CambiarPermisoRolDTO) -> None:
        # 1) Validar rol existe
        rol_existe = await self.rol_repo.exists(dto.rol_id)
        if not rol_existe:
            raise RolNoEncontrado(f"Rol con ID {dto.rol_id} no encontrado")

        # 2) Validar permiso nuevo existe
        permiso_existe = await self.permiso_repo.exists(dto.permiso_nuevo_id)
        if not permiso_existe:
            raise PermisoNoEncontrado(f"Permiso con ID {dto.permiso_nuevo_id} no encontrado")

        # 3) Validar que tenga el permiso anterior asignado
        tiene_anterior = await self.rol_permiso_repo.ya_asignado(
            dto.rol_id, dto.permiso_anterior_id
        )
        if not tiene_anterior:
            raise RolPermisoNoEncontrado(
                f"El rol {dto.rol_id} no tiene asignado el permiso {dto.permiso_anterior_id}"
            )

        # 4) Validar que no tenga ya el nuevo permiso
        ya_tiene_nuevo = await self.rol_permiso_repo.ya_asignado(
            dto.rol_id, dto.permiso_nuevo_id
        )
        if ya_tiene_nuevo:
            raise RolPermisoYaAsignado(
                f"El rol {dto.rol_id} ya tiene asignado el permiso {dto.permiso_nuevo_id}"
            )

        # 5) Revocar permiso anterior
        await self.rol_permiso_repo.revocar(dto.rol_id, dto.permiso_anterior_id)

        # 6) Asignar permiso nuevo
        await self.rol_permiso_repo.asignar(dto.rol_id, dto.permiso_nuevo_id)
