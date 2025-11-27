# app/kernel/application/seguridad/usuarios/cambiar_estado_usuario.py
from __future__ import annotations

from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.errors import UsuarioNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractUserRepository


class CambiarEstadoUsuarioDTO(BaseModel):
    usuario_id: int = Field(..., gt=0)
    activo: bool


class CambiarEstadoUsuario:
    """Caso de uso: Activar o desactivar un usuario."""

    def __init__(self, usuario_repo: AbstractUserRepository):
        self.usuario_repo = usuario_repo

    async def execute(self, dto: CambiarEstadoUsuarioDTO) -> dict:
        usuario = await self.usuario_repo.get_by_id(dto.usuario_id)
        if not usuario:
            raise UsuarioNoEncontrado(f"Usuario con ID {dto.usuario_id} no encontrado")

        await self.usuario_repo.cambiar_estado(dto.usuario_id, dto.activo)
        estado = "activado" if dto.activo else "desactivado"
        return {"message": f"Usuario {estado} exitosamente"}
