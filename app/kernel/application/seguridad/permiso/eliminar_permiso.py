# app/kernel/application/seguridad/permisos/eliminar_permiso.py
from __future__ import annotations

from app.kernel.domain.seguridad.errors import PermisoNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractPermisoRepository


class EliminarPermiso:
    """Caso de uso: Desactivar (soft delete) un permiso."""
    def __init__(self, permiso_repo: AbstractPermisoRepository):
        self.permiso_repo = permiso_repo

    async def execute(self, permiso_id: int) -> None:
        existe = await self.permiso_repo.exists(permiso_id)
        if not existe:
            raise PermisoNoEncontrado(f"Permiso con ID {permiso_id} no encontrado")

        ok = await self.permiso_repo.delete_soft(permiso_id)
        if not ok:
            raise PermisoNoEncontrado(f"No se pudo desactivar el permiso {permiso_id}")
