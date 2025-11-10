# app/kernel/application/seguridad/registrar_usuario.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from app.kernel.domain.seguridad.errors import RolNoEncontrado, CredencialesInvalidas
from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractRolRepository, AbstractHasher
from typing import Protocol

class IUsuarioRolRepository(Protocol):
    async def asignar(self, usuario_id: int, rol_id: int) -> None: ...

class RegistrarUsuarioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sede_id: int
    username: str = Field(min_length=4, max_length=64)
    password: str = Field(min_length=8)
    nombre_completo: str = Field(min_length=3, max_length=160)
    email: str | None = Field(default=None, max_length=120)
    telefono: str | None = Field(default=None, max_length=20)
    rol_nombre: str = Field(default="tutor")

class RegistrarUsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    nombre_completo: str
    email: str | None = None
    sede_id: int
    rol: str

class RegistrarUsuario:
    def __init__(self, usuarios: AbstractUserRepository, roles: AbstractRolRepository, usuarios_roles: IUsuarioRolRepository, hasher: AbstractHasher):
        self.usuarios = usuarios
        self.roles = roles
        self.usuarios_roles = usuarios_roles
        self.hasher = hasher

    async def execute(self, req: RegistrarUsuarioRequest) -> RegistrarUsuarioResponse:
        if await self.usuarios.get_by_username(req.username):
            raise CredencialesInvalidas("Nombre de usuario en uso")
        if req.email and await self.usuarios.get_by_email(req.email):
            raise CredencialesInvalidas("Email en uso")
        rol = await self.roles.get_by_nombre(req.rol_nombre)
        if not rol:
            raise RolNoEncontrado()
        hashed = self.hasher.hash_password(req.password)
        u = await self.usuarios.crear(username=req.username, password_hash=hashed, nombre_completo=req.nombre_completo,
                                      email=req.email, telefono=req.telefono, sede_id=req.sede_id)
        await self.usuarios_roles.asignar(u.id, rol.id)
        return RegistrarUsuarioResponse(id=u.id, username=u.username, nombre_completo=u.nombre_completo,
                                        email=u.email, sede_id=u.sede_id, rol=rol.nombre)
