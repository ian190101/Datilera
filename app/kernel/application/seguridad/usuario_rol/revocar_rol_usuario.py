# app/kernel/application/seguridad/usuario_rol/revocar_rol_usuario.py
from __future__ import annotations

from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.errors import UsuarioRolNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractUsuarioRolRepository


class RevocarRolUsuarioDTO(BaseModel):
    usuario_id: int = Field(..., gt=0)
    rol_id: int = Field(..., gt=0)


class RevocarRolUsuario:
    """Caso de uso: Revocar un rol de un usuario."""

    def __init__(self, usuario_rol_repo: AbstractUsuarioRolRepository):
        self.usuario_rol_repo = usuario_rol_repo

    async def execute(self, dto: RevocarRolUsuarioDTO) -> None:
        ok = await self.usuario_rol_repo.revocar(dto.usuario_id, dto.rol_id)
        if not ok:
            raise UsuarioRolNoEncontrado(
                f"No se encontró asignación del rol {dto.rol_id} al usuario {dto.usuario_id}"
            )
