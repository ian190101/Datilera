# app/kernel/application/seguridad/login.py
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Protocol, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.kernel.domain.seguridad.errors import CredencialesInvalidas, UsuarioInactivo
from app.kernel.domain.seguridad.ports import (
    AbstractUserRepository,
    AbstractHasher,
    AbstractTokenService,
)

from app.kernel.domain.seguridad.user_entidad import Usuario
import uuid


class IRateLimiter(Protocol):
    async def check(self, key: str) -> Optional[int]: ...  # devuelve segundos a esperar si excede
    async def hit(self, key: str) -> None: ...
    async def reset(self, key: str) -> None: ...


class ISesionRepository(Protocol):
    async def crear(self, usuario_id: int, refresh_token: str, expira_en: datetime) -> None: ...


class LoginRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8)

    # Opcionales (tu API los inyecta con model_copy(update=...))
    ip: Optional[str] = None
    user_agent: Optional[str] = None


class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    usuario: Usuario


class Login:
    def __init__(
        self,
        usuarios: AbstractUserRepository,
        hasher: AbstractHasher,
        tokens: AbstractTokenService,
        sesiones: ISesionRepository,
        limiter: IRateLimiter,
        refresh_ttl_min: int = 60 * 24 * 30,
    ):
        self.usuarios = usuarios
        self.hasher = hasher
        self.tokens = tokens
        self.sesiones = sesiones
        self.limiter = limiter
        self.refresh_ttl_min = refresh_ttl_min

    async def execute(self, req: LoginRequest) -> LoginResponse:
        username = req.username.strip()
        key = f"login:{username}:{req.ip or 'unknown'}"

        wait = await self.limiter.check(key)
        if wait:
            raise CredencialesInvalidas(f"Demasiados intentos, reintente en {wait}s")

        user = await self.usuarios.get_by_username(username)

        # En tu proyecto hay indicios de que el hash puede estar en "hashpassword"
        # (por ejemplo en registros desde routes.py), así que hacemos fallback.
        hashed = getattr(user, "contrasena", None) if user else None
        if not hashed and user:
            hashed = getattr(user, "hashpassword", None)

        if (not user) or (not hashed) or (not self.hasher.verify_password(req.password, hashed)):
            await self.limiter.hit(key)

            raise CredencialesInvalidas()

        if not user.activo:
            await self.limiter.reset(key)

            raise UsuarioInactivo()

        # permisos efectivos (recurso:accion)
        permisos = {p.nombre_completo for r in user.roles for p in r.permisos}

        jti = str(uuid.uuid4())
        access = self.tokens.create_access_token(
            user_id=user.id,
            sede_id=user.sede_id,
            permisos=list(permisos),
            roles=[rol.nombre for rol in user.roles],
        )
        refresh = self.tokens.create_refresh_token(user_id=user.id, jti=jti)

        expira = datetime.now(timezone.utc) + timedelta(minutes=self.refresh_ttl_min)
        await self.sesiones.crear(user.id, refresh, expira)

        await self.limiter.reset(key)

        # Convertimos el usuario SQLAlchemy -> Pydantic
        usuario_convertido = Usuario.model_validate(user)

        return LoginResponse(
            access_token=access,
            refresh_token=refresh,
            usuario=usuario_convertido,
        )
