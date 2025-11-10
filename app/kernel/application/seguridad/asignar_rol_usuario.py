# app/kernel/application/seguridad/asignar_rol_usuario.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from app.kernel.domain.seguridad.errors import UsuarioNoEncontrado, RolNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractRolRepository
from app.kernel.domain.auditoria.ports import IAuditoriaAccionRepo
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion
from typing import Protocol

class IUsuarioRolRepository(Protocol):
    async def ya_asignado(self, usuario_id: int, rol_id: int) -> bool: ...
    async def asignar(self, usuario_id: int, rol_id: int) -> None: ...

class AsignarRolUsuarioRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    usuario_id: int = Field(gt=0)
    rol_id: int = Field(gt=0)

class AsignarRolUsuario:
    def __init__(self, usuarios: AbstractUserRepository, roles: AbstractRolRepository, usuarios_roles: IUsuarioRolRepository, auditoria: IAuditoriaAccionRepo | None = None):
        self.usuarios = usuarios
        self.roles = roles
        self.usuarios_roles = usuarios_roles
        self.auditoria = auditoria 

    async def execute(self, req: AsignarRolUsuarioRequest) -> None:
        user = await self.usuarios.get_by_id(req.usuario_id)
        if not user:
            raise UsuarioNoEncontrado()
        rol = await self.roles.get_by_id(req.rol_id)
        if not rol:
            raise RolNoEncontrado()
        if await self.usuarios_roles.ya_asignado(req.usuario_id, req.rol_id):
            return  # idempotente
        await self.usuarios_roles.asignar(req.usuario_id, req.rol_id)
        if self.auditoria:
            await self.auditoria.registrar(AuditoriaAccion(
                usuario_id=user.id, sede_id=user.sede_id, entidad="usuarios_roles", entidad_id=str(req.usuario_id),
                accion="assign_role", ip=req.ip, user_agent=req.user_agent,
                datos_despues={"rol_id": req.rol_id}
            ))

