from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Protocol
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion
from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort
from app.kernel.domain.seguridad.errors import (
    TokenExpirado,
    TokenInvalido,
    UsuarioInactivo,
    UsuarioNoEncontrado,
)
from app.kernel.domain.seguridad.ports import AbstractTokenService, AbstractUserRepository


class IRevocadosRepository(Protocol):
    async def esta_revocado(self, jti: str) -> bool: ...
    async def revocar(self, jti: str) -> None: ...


class ISesionRepository(Protocol):
    async def crear(self, usuario_id: int, refresh_token: str, expira_en: datetime) -> None: ...
    async def eliminar_por_refresh(self, refresh_token: str) -> bool: ...


class RefreshRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    refresh_token: str = Field(min_length=20)
    ip: str | None = None
    user_agent: str | None = None


class RefreshResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Refresh:
    def __init__(
        self,
        usuarios: AbstractUserRepository,
        tokens: AbstractTokenService,
        revocados: IRevocadosRepository,
        sesiones: ISesionRepository,
        refresh_expire_days: int = 7,
        auditoria: AuditoriaAccionRepositoryPort | None = None,
    ) -> None:
        self.usuarios = usuarios
        self.tokens = tokens
        self.revocados = revocados
        self.sesiones = sesiones
        self.refresh_expire_days = refresh_expire_days
        self.auditoria = auditoria

    async def execute(self, req: RefreshRequest) -> RefreshResponse:
        try:
            payload = self.tokens.decode_token(req.refresh_token)
        except Exception as exc:
            raise TokenInvalido() from exc
        if not payload or payload.get("type") != "refresh":
            raise TokenInvalido()

        old_jti = payload.get("jti")
        uid = payload.get("sub")
        if not old_jti or not uid or await self.revocados.esta_revocado(old_jti):
            raise TokenExpirado()

        user = await self.usuarios.get_by_id(int(uid))
        if not user:
            raise UsuarioNoEncontrado()
        if not user.activo:
            raise UsuarioInactivo()

        permisos = {p.nombre_completo for r in user.roles for p in r.permisos}
        new_jti = str(uuid.uuid4())
        new_access = self.tokens.create_access_token(
            user_id=user.id,
            sede_id=user.sede_id,
            permisos=list(permisos),
            roles=[rol.nombre for rol in user.roles],
        )
        new_refresh = self.tokens.create_refresh_token(user_id=user.id, jti=new_jti)

        # La rotación invalida el token consumido y persiste únicamente la nueva huella.
        await self.sesiones.eliminar_por_refresh(req.refresh_token)
        await self.revocados.revocar(old_jti)
        await self.sesiones.crear(
            user.id,
            new_refresh,
            datetime.now(timezone.utc) + timedelta(days=self.refresh_expire_days),
        )

        if self.auditoria:
            await self.auditoria.registrar(
                AuditoriaAccion(
                    usuario_id=user.id,
                    sede_id=user.sede_id,
                    entidad="auth",
                    entidad_id=str(user.id),
                    accion="refresh",
                    ip=req.ip,
                    user_agent=req.user_agent,
                    datos_despues={"resultado": "ok"},
                )
            )

        return RefreshResponse(access_token=new_access, refresh_token=new_refresh)
