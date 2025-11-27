# app/kernel/application/seguridad/usuario_rol/listar_roles_usuario.py
from __future__ import annotations

from typing import Any

from app.kernel.domain.seguridad.errors import UsuarioNoEncontrado
from app.kernel.domain.seguridad.ports import (
    AbstractUserRepository,
    AbstractUsuarioRolRepository,
)


class ListarRolesUsuario:
    """Caso de uso: Listar roles asignados a un usuario."""

    def __init__(
        self,
        usuario_repo: AbstractUserRepository,
        usuario_rol_repo: AbstractUsuarioRolRepository,
    ):
        self.usuario_repo = usuario_repo
        self.usuario_rol_repo = usuario_rol_repo

    async def execute(self, usuario_id: int) -> dict[str, Any]:
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontrado(f"Usuario con ID {usuario_id} no encontrado")

        asignaciones = await self.usuario_rol_repo.listar_por_usuario(usuario_id)
        return {
            "usuario_id": usuario_id,
            "roles": [a.model_dump() for a in asignaciones],
        }
