# app/kernel/application/seguridad/cambiar_contrasena.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from app.kernel.domain.seguridad.errors import UsuarioNoEncontrado, CredencialesInvalidas
from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractHasher

class CambiarContrasenaRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    usuario_id: int
    contrasena_actual: str = Field(min_length=8)
    contrasena_nueva: str = Field(min_length=8)

class CambiarContrasena:
    def __init__(self, usuarios: AbstractUserRepository, hasher: AbstractHasher):
        self.usuarios = usuarios
        self.hasher = hasher
    async def execute(self, req: CambiarContrasenaRequest) -> None:
        u = await self.usuarios.get_by_id(req.usuario_id)
        if not u:
            raise UsuarioNoEncontrado()
        if not self.hasher.verify_password(req.contrasena_actual, u.contrasena):
            raise CredencialesInvalidas("Contraseña actual incorrecta")
        hashed = self.hasher.hash_password(req.contrasena_nueva)
        await self.usuarios.actualizar_password(u.id, hashed)
