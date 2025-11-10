# app/kernel/application/seguridad/asignar_permiso_rol.py
from __future__ import annotations
from typing import Optional, Protocol
from pydantic import BaseModel, ConfigDict, Field
from app.kernel.domain.seguridad.errors import RolNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractRolRepository
from app.kernel.domain.seguridad.permiso_entidad import Permiso
from app.kernel.domain.auditoria.ports import IAuditoriaAccionRepo
from app.kernel.domain.auditoria.auditoria_accion_entidad import AuditoriaAccion

class IPermisoRepository(Protocol):
    async def get_by_id(self, permiso_id: int) -> Optional[Permiso]: ...
    async def rol_tiene_permiso(self, rol_id: int, permiso_id: int) -> bool: ...
    async def asignar_a_rol(self, rol_id: int, permiso_id: int) -> None: ...

class AsignarPermisoRolRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rol_id: int = Field(gt=0)
    permiso_id: int = Field(gt=0)

class AsignarPermisoRol:
    def __init__(self, roles: AbstractRolRepository, permisos: IPermisoRepository, auditoria: IAuditoriaAccionRepo | None = None):
        self.roles = roles
        self.permisos = permisos
        self.auditoria = auditoria

    async def execute(
        self,
        req: AsignarPermisoRolRequest,
        *,
        actor_id: int | None = None,
        sede_id: int | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        rol = await self.roles.get_by_id(req.rol_id)
        if not rol:
            raise RolNoEncontrado(f"Rol id={req.rol_id} no existe")
        permiso = await self.permisos.get_by_id(req.permiso_id)
        if not permiso:
            raise ValueError("Permiso no encontrado")
        if await self.permisos.rol_tiene_permiso(req.rol_id, req.permiso_id):
            return
        await self.permisos.asignar_a_rol(req.rol_id, req.permiso_id)
        if self.auditoria:
            await self.auditoria.registrar(
                AuditoriaAccion(
                    usuario_id=actor_id,
                    sede_id=sede_id,
                    entidad="roles",
                    entidad_id=str(req.rol_id),
                    accion="assign_permission",
                    ip=ip,
                    user_agent=user_agent,
                    datos_despues={"permiso_id": req.permiso_id},
                )
            )
