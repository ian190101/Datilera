# app/kernel/application/seguridad/update_rol.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from app.kernel.domain.seguridad.errors import RolNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractRolRepository

class ActualizarRolRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: str | None = None
    activo: bool

class ActualizarRol:
    def __init__(self, roles: AbstractRolRepository):
        self.roles = roles
    async def execute(self, rol_id: int, req: ActualizarRolRequest) -> None:
        rol = await self.roles.get_by_id(rol_id)
        if not rol:
            raise RolNoEncontrado()
        await self.roles.actualizar(rol_id, req.model_dump())
