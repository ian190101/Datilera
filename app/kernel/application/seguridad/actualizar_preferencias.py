# app/kernel/application/seguridad/actualizar_preferencias.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from app.kernel.domain.seguridad.ports import AbstractUserRepository
from app.kernel.domain.seguridad.errors import UsuarioNoEncontrado

class ActualizarPreferenciasRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tema: str | None = None
    notificaciones: bool | None = None
    idioma: str | None = None

class ActualizarPreferencias:
    def __init__(self, usuarios: AbstractUserRepository): self.usuarios = usuarios
    async def execute(self, usuario_id: int, req: ActualizarPreferenciasRequest) -> None:
        u = await self.usuarios.get_by_id(usuario_id)
        if not u: raise UsuarioNoEncontrado()
        await self.usuarios.actualizar_preferencias(usuario_id, req.model_dump(exclude_none=True))
