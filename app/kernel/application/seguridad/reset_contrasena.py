# app/kernel/application/seguridad/reset_contrasena.py
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ConfigDict, Field
from typing import Protocol, Optional
from app.kernel.domain.seguridad.errors import UsuarioNoEncontrado, CredencialesInvalidas
from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractHasher

class IResetRepo(Protocol):
    async def crear_token(self, usuario_id: int, token: str, expira_en: datetime) -> None: ...
    async def validar_y_consumir(self, token: str) -> Optional[int]: ...

class SolicitarResetRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str = Field(min_length=5, max_length=120)

class EjecutarResetRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    token: str = Field(min_length=20)
    nueva_contrasena: str = Field(min_length=8)

class SolicitarResetContrasena:
    def __init__(self, usuarios: "AbstractUserRepository", resets: IResetRepo):
        self.usuarios = usuarios
        self.resets = resets
    async def execute(self, req: SolicitarResetRequest) -> None:
        u = await self.usuarios.get_by_email(req.email)
        if not u:
            return
        t = f"rst-{u.id}-{int(datetime.now(timezone.utc).timestamp())}"
        await self.resets.crear_token(u.id, t, datetime.now(timezone.utc) + timedelta(minutes=30))

class EjecutarResetContrasena:
    def __init__(self, usuarios: "AbstractUserRepository", resets: IResetRepo, hasher: "AbstractHasher"):
        self.usuarios = usuarios
        self.resets = resets
        self.hasher = hasher
    async def execute(self, req: EjecutarResetRequest) -> None:
        uid = await self.resets.validar_y_consumir(req.token)
        if not uid:
            raise CredencialesInvalidas("Token inválido o expirado")
        hashed = self.hasher.hash_password(req.nueva_contrasena)
        await self.usuarios.actualizar_password(uid, hashed)
