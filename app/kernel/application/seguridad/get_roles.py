# app/kernel/application/seguridad/get_roles.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import List
from app.kernel.application.seguridad.crear_rol import RolDTO
from app.kernel.domain.seguridad.ports import AbstractRolRepository

class GetRolesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    roles: List[RolDTO]

class GetRoles:
    def __init__(self, roles: AbstractRolRepository):
        self.roles = roles
    async def execute(self) -> GetRolesResponse:
        data = await self.roles.listar()
        return GetRolesResponse(roles=[RolDTO.model_validate(x) for x in data])
