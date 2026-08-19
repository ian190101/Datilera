# app/kernel/application/seguridad/cerrar_sesion.py
from __future__ import annotations
from typing import Protocol
from pydantic import BaseModel, ConfigDict, Field
from app.kernel.domain.seguridad.errors import TokenInvalido
from app.kernel.domain.seguridad.ports import AbstractTokenService
from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion

class ISesionRepository(Protocol):
    async def eliminar_por_refresh(self, refresh_token: str) -> bool: ...

class IRevocadosRepository(Protocol):
    async def revocar(self, jti: str) -> None: ...

class CerrarSesionRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    refresh_token: str = Field(min_length=20)
    ip: str | None = None
    user_agent: str | None = None
    usuario_id: int | None = None
    sede_id: int | None = None

class CerrarSesion:
    def __init__(self, sesiones: ISesionRepository, tokens: AbstractTokenService, revocados: IRevocadosRepository, auditoria: AuditoriaAccionRepositoryPort | None = None):
        self.sesiones = sesiones
        self.tokens = tokens
        self.revocados = revocados
        self.auditoria = auditoria 

    async def execute(self, req: CerrarSesionRequest) -> None:
        try:
            payload = self.tokens.decode_token(req.refresh_token)
        except Exception:
            # Logout es idempotente: una cookie vencida no debe producir error 500.
            return
        if not payload or payload.get("type") != "refresh":
            raise TokenInvalido()
        jti = payload.get("jti")
        await self.sesiones.eliminar_por_refresh(req.refresh_token)
        if jti:
            await self.revocados.revocar(jti)
        if self.auditoria:
            usuario_id = req.usuario_id or int(payload.get("sub"))
            await self.auditoria.registrar(AuditoriaAccion(
                usuario_id=usuario_id, sede_id=req.sede_id, entidad="auth",
                entidad_id=str(usuario_id), accion="logout", ip=req.ip,
                user_agent=req.user_agent, datos_despues={"resultado": "ok"}
            ))
