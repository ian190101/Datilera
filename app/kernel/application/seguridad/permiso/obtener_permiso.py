# app/kernel/application/seguridad/permisos/obtener_permiso.py
from __future__ import annotations

from app.kernel.domain.seguridad.permiso_entidad import Permiso
from app.kernel.domain.seguridad.errors import PermisoNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractPermisoRepository


class ObtenerPermiso:
    """Caso de uso: Obtener permiso por ID."""
    def __init__(self, permiso_repo: AbstractPermisoRepository):
        self.permiso_repo = permiso_repo

    async def execute(self, permiso_id: int) -> Permiso:
        permiso = await self.permiso_repo.get(permiso_id)
        if not permiso:
            raise PermisoNoEncontrado(f"Permiso con ID {permiso_id} no encontrado")
        return permiso
