# app/kernel/application/seguridad/usuarios/editar_usuario.py
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, EmailStr

from app.kernel.domain.seguridad.errors import UsuarioNoEncontrado, UsuarioEmailDuplicado
from app.kernel.domain.seguridad.ports import AbstractUserRepository


class EditarUsuarioDTO(BaseModel):
    usuario_id: int = Field(..., gt=0)
    nombre_completo: Optional[str] = Field(None, max_length=160)
    email: Optional[str] = Field(None, max_length=120)
    telefono: Optional[str] = Field(None, max_length=20)
    foto_perfil_url: Optional[str] = Field(None, max_length=255)


class EditarUsuario:
    """Caso de uso: Editar perfil de usuario (sin cambio de username/rol)."""

    def __init__(self, usuario_repo: AbstractUserRepository):
        self.usuario_repo = usuario_repo

    async def execute(self, dto: EditarUsuarioDTO) -> dict:
        # 1) Validar usuario existe
        usuario = await self.usuario_repo.get_by_id(dto.usuario_id)
        if not usuario:
            raise UsuarioNoEncontrado(f"Usuario con ID {dto.usuario_id} no encontrado")

        # 2) Validar email único si cambia
        if dto.email and dto.email != usuario.rol.nombre:
            existente = await self.usuario_repo.get_by_email(dto.email)
            if existente and existente.id != dto.usuario_id:
                raise UsuarioEmailDuplicado(f"El email '{dto.email}' ya está registrado")

        # 3) Actualizar solo campos proporcionados
        data = {k: v for k, v in dto.model_dump().items() if k != "usuario_id" and v is not None}
        if data:
            await self.usuario_repo.update_perfil(dto.usuario_id, data)

        return {"message": "Usuario actualizado exitosamente"}
