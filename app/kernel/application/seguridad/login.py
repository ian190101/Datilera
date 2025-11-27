# app/kernel/application/seguridad/login.py
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import List, Protocol, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.kernel.domain.seguridad.errors import CredencialesInvalidas, UsuarioInactivo
from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractHasher, AbstractTokenService
from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion

class IRateLimiter(Protocol):
    async def check(self, key: str) -> Optional[int]: ...   # devuelve segundos a esperar si excede
    async def hit(self, key: str) -> None: ...
    async def reset(self, key: str) -> None: ...

class ISesionRepository(Protocol):
    async def crear(self, usuario_id: int, refresh_token: str, expira_en: datetime) -> None: ...

class LoginRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8)

class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class Login:
    def __init__(self, usuarios: AbstractUserRepository, hasher: AbstractHasher, tokens: AbstractTokenService,
                 sesiones: ISesionRepository, limiter: IRateLimiter, refresh_ttl_min: int = 60*24*30,  auditoria: Optional[AuditoriaAccionRepositoryPort] = None):
        self.usuarios = usuarios
        self.hasher = hasher
        self.tokens = tokens
        self.sesiones = sesiones
        self.limiter = limiter
        self.refresh_ttl_min = refresh_ttl_min
        self.auditoria = auditoria

    async def execute(self, req: LoginRequest) -> LoginResponse:
        key = f"login:{req.username}"
        wait = await self.limiter.check(key)
        if wait:
            raise CredencialesInvalidas(f"Demasiados intentos, reintente en {wait}s")
        user = await self.usuarios.get_by_username(req.username)
        if not user or not self.hasher.verify_password(req.password, user.contrasena):
            await self.limiter.hit(key)
            if self.auditoria:
                await self.auditoria.registrar(AuditoriaAccion(
                    usuario_id=None, sede_id=None, entidad="auth", entidad_id=None, accion="login",
                    ip=req.ip, user_agent=req.user_agent, datos_despues={"resultado": "fallido"}
                ))
            raise CredencialesInvalidas()
        if not user.activo:
            await self.limiter.reset(key)
            if self.auditoria:
                await self.auditoria.registrar(AuditoriaAccion(
                    usuario_id=user.id, sede_id=user.sede_id, entidad="auth", entidad_id=str(user.id), accion="login",
                    ip=req.ip, user_agent=req.user_agent, datos_despues={"resultado": "usuario_inactivo"}
                ))

            raise UsuarioInactivo()
        # permisos efectivos (recurso:accion)
        permisos = {p.nombre_completo for r in user.roles for p in r.permisos}
        jti = f"{user.id}:{int(datetime.now(timezone.utc).timestamp())}"
        access = self.tokens.create_access_token(user_id=user.id, sede_id=user.sede_id, permisos=list(permisos))
        refresh = self.tokens.create_refresh_token(user_id=user.id, jti=jti)
        expira = datetime.now(timezone.utc) + timedelta(minutes=self.refresh_ttl_min)
        await self.sesiones.crear(user.id, refresh, expira)
        await self.limiter.reset(key)
        return LoginResponse(access_token=access, refresh_token=refresh)
