# app/kernel/application/seguridad/roles/obtener_rol.py
from __future__ import annotations

from app.kernel.domain.seguridad.rol_entidad import Rol
from app.kernel.domain.seguridad.errors import RolNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractRolRepository


class ObtenerRol:
    """Caso de uso: Obtener rol por ID."""
    def __init__(self, rol_repo: AbstractRolRepository):
        self.rol_repo = rol_repo

    async def execute(self, rol_id: int) -> Rol:
        rol = await self.rol_repo.get(rol_id)
        if not rol:
            raise RolNoEncontrado(f"Rol con ID {rol_id} no encontrado")
        return rol
