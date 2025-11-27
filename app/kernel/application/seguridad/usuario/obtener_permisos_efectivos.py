# app/kernel/application/seguridad/usuarios/obtener_permisos_efectivos.py
from __future__ import annotations

from typing import Any

from app.kernel.domain.seguridad.errors import UsuarioNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractUserRepository


class ObtenerPermisosEfectivos:
    """Caso de uso: Obtener permisos efectivos de un usuario."""

    def __init__(self, usuario_repo: AbstractUserRepository):
        self.usuario_repo = usuario_repo

    async def execute(self, usuario_id: int) -> dict[str, Any]:
        usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontrado(f"Usuario con ID {usuario_id} no encontrado")

        permisos = await self.usuario_repo.get_permisos_efectivos(usuario_id)
        return {
            "usuario_id": usuario_id,
            "permisos": [p.model_dump() for p in permisos],
        }
