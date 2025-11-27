# app/kernel/application/seguridad/usuario_rol/cambiar_rol_usuario.py
from __future__ import annotations

from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.errors import (
    UsuarioNoEncontrado,
    RolNoEncontrado,
    UsuarioRolNoEncontrado,
    UsuarioRolYaAsignado,
)
from app.kernel.domain.seguridad.ports import (
    AbstractUserRepository,
    AbstractRolRepository,
    AbstractUsuarioRolRepository,
)


class CambiarRolUsuarioDTO(BaseModel):
    usuario_id: int = Field(..., gt=0)
    rol_anterior_id: int = Field(..., gt=0)
    rol_nuevo_id: int = Field(..., gt=0)


class CambiarRolUsuario:
    """Caso de uso: Cambiar rol asignado a un usuario."""

    def __init__(
        self,
        usuario_repo: AbstractUserRepository,
        rol_repo: AbstractRolRepository,
        usuario_rol_repo: AbstractUsuarioRolRepository,
    ):
        self.usuario_repo = usuario_repo
        self.rol_repo = rol_repo
        self.usuario_rol_repo = usuario_rol_repo

    async def execute(self, dto: CambiarRolUsuarioDTO) -> None:
        # 1) Validar usuario existe
        usuario = await self.usuario_repo.get_by_id(dto.usuario_id)
        if not usuario:
            raise UsuarioNoEncontrado(f"Usuario con ID {dto.usuario_id} no encontrado")

        # 2) Validar rol nuevo existe
        rol_existe = await self.rol_repo.exists(dto.rol_nuevo_id)
        if not rol_existe:
            raise RolNoEncontrado(f"Rol con ID {dto.rol_nuevo_id} no encontrado")

        # 3) Validar que tenga el rol anterior asignado
        tiene_anterior = await self.usuario_rol_repo.ya_asignado(
            dto.usuario_id, dto.rol_anterior_id
        )
        if not tiene_anterior:
            raise UsuarioRolNoEncontrado(
                f"El usuario {dto.usuario_id} no tiene asignado el rol {dto.rol_anterior_id}"
            )

        # 4) Validar que no tenga ya el nuevo rol
        ya_tiene_nuevo = await self.usuario_rol_repo.ya_asignado(
            dto.usuario_id, dto.rol_nuevo_id
        )
        if ya_tiene_nuevo:
            raise UsuarioRolYaAsignado(
                f"El usuario {dto.usuario_id} ya tiene asignado el rol {dto.rol_nuevo_id}"
            )

        # 5) Revocar rol anterior
        await self.usuario_rol_repo.revocar(dto.usuario_id, dto.rol_anterior_id)

        # 6) Asignar rol nuevo
        await self.usuario_rol_repo.asignar(dto.usuario_id, dto.rol_nuevo_id)
