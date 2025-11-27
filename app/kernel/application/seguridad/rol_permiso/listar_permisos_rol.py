# app/kernel/application/seguridad/rol_permiso/listar_permisos_rol.py
from __future__ import annotations

from typing import Any

from app.kernel.domain.seguridad.errors import RolNoEncontrado
from app.kernel.domain.seguridad.ports import (
    AbstractRolRepository,
    AbstractRolPermisoRepository,
)


class ListarPermisosRol:
    """Caso de uso: Listar permisos asignados a un rol."""

    def __init__(
        self,
        rol_repo: AbstractRolRepository,
        rol_permiso_repo: AbstractRolPermisoRepository,
    ):
        self.rol_repo = rol_repo
        self.rol_permiso_repo = rol_permiso_repo

    async def execute(self, rol_id: int) -> dict[str, Any]:
        rol_existe = await self.rol_repo.exists(rol_id)
        if not rol_existe:
            raise RolNoEncontrado(f"Rol con ID {rol_id} no encontrado")

        asignaciones = await self.rol_permiso_repo.listar_por_rol(rol_id)
        return {
            "rol_id": rol_id,
            "permisos": [a.model_dump() for a in asignaciones],
        }
