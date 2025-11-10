# app/kernel/application/seguridad/crear_usuario.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.kernel.domain.seguridad.errors import RolNoEncontrado, CredencialesInvalidas
from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractRolRepository, AbstractHasher

class CrearUsuarioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8)
    nombre_completo: str = Field(min_length=3, max_length=160)
    email: str | None = Field(default=None, max_length=120)
    telefono: str | None = Field(default=None, max_length=20)
    sede_id: int

class UsuarioDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    nombre_completo: str
    email: str | None = None
    telefono: str | None = None
    sede_id: int
    activo: bool

class CrearUsuario:
    def __init__(self, usuarios: AbstractUserRepository, roles: AbstractRolRepository, hasher: AbstractHasher):
        self.usuarios = usuarios
        self.roles = roles
        self.hasher = hasher

    async def execute(self, req: CrearUsuarioRequest) -> UsuarioDTO:
        if await self.usuarios.get_by_username(req.username):
            raise CredencialesInvalidas("Nombre de usuario en uso")
        if req.email and await self.usuarios.get_by_email(req.email):
            raise CredencialesInvalidas("Email en uso")
        hashed = self.hasher.hash_password(req.password)
        user = await self.usuarios.crear(username=req.username, password_hash=hashed,
                                         nombre_completo=req.nombre_completo, email=req.email,
                                         telefono=req.telefono, sede_id=req.sede_id)
        return UsuarioDTO.model_validate(user)
