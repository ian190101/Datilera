# app/kernel/application/seguridad/roles/desactivarar_rol.py
from __future__ import annotations

from app.kernel.domain.seguridad.errors import RolNoEncontrado, RolEnUso
from app.kernel.domain.seguridad.ports import AbstractRolRepository


class DesactivarRol:
    """Caso de uso: Desactivar (soft delete) un rol."""
    def __init__(self, rol_repo: AbstractRolRepository):
        self.rol_repo = rol_repo

    async def execute(self, rol_id: int) -> None:
        existe = await self.rol_repo.exists(rol_id)
        if not existe:
            raise RolNoEncontrado(f"Rol con ID {rol_id} no encontrado")

        ok = await self.rol_repo.delete_soft(rol_id)
        if not ok:
            # El repositorio debe devolver False si el rol está asignado a usuarios (en uso)
            raise RolEnUso(f"No se puede eliminar el rol {rol_id} porque está en uso")
