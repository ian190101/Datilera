# app/kernel/application/seguridad/usuario_rol/asignar_rol_usuario.py
from __future__ import annotations

from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.errors import (
    UsuarioNoEncontrado,
    RolNoEncontrado,
    UsuarioRolYaAsignado,
)
from app.kernel.domain.seguridad.ports import (
    AbstractUserRepository,
    AbstractRolRepository,
    AbstractUsuarioRolRepository,
)


class AsignarRolUsuarioDTO(BaseModel):
    usuario_id: int = Field(..., gt=0)
    rol_id: int = Field(..., gt=0)


class AsignarRolUsuario:
    """Caso de uso: Asignar un rol a un usuario."""

    def __init__(
        self,
        usuario_repo: AbstractUserRepository,
        rol_repo: AbstractRolRepository,
        usuario_rol_repo: AbstractUsuarioRolRepository,
    ):
        self.usuario_repo = usuario_repo
        self.rol_repo = rol_repo
        self.usuario_rol_repo = usuario_rol_repo

    async def execute(self, dto: AsignarRolUsuarioDTO) -> None:
        # 1) Validar usuario existe
        usuario = await self.usuario_repo.get_by_id(dto.usuario_id)
        if not usuario:
            raise UsuarioNoEncontrado(f"Usuario con ID {dto.usuario_id} no encontrado")

        # 2) Validar rol existe
        rol_existe = await self.rol_repo.exists(dto.rol_id)
        if not rol_existe:
            raise RolNoEncontrado(f"Rol con ID {dto.rol_id} no encontrado")

        # 3) Validar que no esté ya asignado
        ya_tiene = await self.usuario_rol_repo.ya_asignado(dto.usuario_id, dto.rol_id)
        if ya_tiene:
            raise UsuarioRolYaAsignado(
                f"El usuario {dto.usuario_id} ya tiene asignado el rol {dto.rol_id}"
            )

        # 4) Asignar
        await self.usuario_rol_repo.asignar(dto.usuario_id, dto.rol_id)
