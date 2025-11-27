# app/kernel/application/seguridad/refresh.py
from __future__ import annotations
from typing import Protocol, Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.kernel.domain.seguridad.errors import TokenInvalido, TokenExpirado, UsuarioNoEncontrado, UsuarioInactivo
from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractTokenService
from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion

class IRevocadosRepository(Protocol):
    async def esta_revocado(self, jti: str) -> bool: ...
    async def revocar(self, jti: str) -> None: ...

class RefreshRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    refresh_token: str = Field(min_length=20)

class RefreshResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class Refresh:
    def __init__(self, usuarios: AbstractUserRepository, tokens: AbstractTokenService, revocados: IRevocadosRepository,  auditoria: AuditoriaAccionRepositoryPort | None = None):
        self.usuarios = usuarios
        self.tokens = tokens
        self.revocados = revocados
        self.auditoria = auditoria

    async def execute(self, req: RefreshRequest) -> RefreshResponse:
        payload = self.tokens.decode_token(req.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise TokenInvalido()
        jti = payload.get("jti")
        uid = payload.get("sub")
        if await self.revocados.esta_revocado(jti):
            if self.auditoria:
                await self.auditoria.registrar(AuditoriaAccion(
                usuario_id=user.id, sede_id=user.sede_id, entidad="auth", entidad_id=str(user.id),
                accion="refresh", ip=req.ip, user_agent=req.user_agent, datos_despues={"resultado": "ok"}
            ))
            raise TokenExpirado()
        user = await self.usuarios.get_by_id(int(uid))
        if not user:
            raise UsuarioNoEncontrado()
        if not user.activo:
            raise UsuarioInactivo()
        permisos = {p.nombre_completo for r in user.roles for p in r.permisos}
        new_access = self.tokens.create_access_token(user_id=user.id, sede_id=user.sede_id, permisos=list(permisos))
        new_refresh = self.tokens.create_refresh_token(user_id=user.id, jti=jti)  # rotación conservando JTI
        await self.revocados.revocar(jti)  # opcional: revocar anterior si usas rotate-on-use estricta
        return RefreshResponse(access_token=new_access, refresh_token=new_refresh)
