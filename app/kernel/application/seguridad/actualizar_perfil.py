# app/kernel/application/seguridad/actualizar_perfil.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from app.kernel.domain.seguridad.errors import UsuarioNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractUserRepository

class ActualizarPerfilRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nombre_usuario: str | None = Field(default=None, min_length=3, max_length=64)
    foto_perfil: str | None = None

class ActualizarPerfil:
    def __init__(self, usuarios: AbstractUserRepository): self.usuarios = usuarios
    async def execute(self, usuario_id: int, req: ActualizarPerfilRequest) -> None:
        u = await self.usuarios.get_by_id(usuario_id)
        if not u: raise UsuarioNoEncontrado()
        await self.usuarios.actualizar_perfil(usuario_id, req.model_dump(exclude_none=True))
