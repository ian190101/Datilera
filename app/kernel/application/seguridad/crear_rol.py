# app/kernel/application/seguridad/crear_rol.py
from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field
from app.kernel.domain.seguridad.errors import RolNoEncontrado
from app.kernel.domain.seguridad.ports import AbstractRolRepository

class CrearRolRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: str | None = None

class RolDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    descripcion: str | None = None
    activo: bool = True
    creado_en: datetime

class CrearRol:
    def __init__(self, roles: AbstractRolRepository):
        self.roles = roles
    async def execute(self, req: CrearRolRequest) -> RolDTO:
        rol = await self.roles.crear(nombre=req.nombre, descripcion=req.descripcion, creado_en=datetime.now(timezone.utc))
        return RolDTO.model_validate(rol)
