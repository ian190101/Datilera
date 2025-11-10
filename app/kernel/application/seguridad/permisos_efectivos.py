# app/kernel/application/seguridad/permisos_efectivos.py
from __future__ import annotations
from typing import List
from pydantic import BaseModel, ConfigDict
from app.kernel.domain.seguridad.ports import AbstractUserRepository

class PermisosEfectivosResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    usuario_id: int
    sede_id: int
    permisos: List[str]

class ObtenerPermisosEfectivos:
    def __init__(self, usuarios: AbstractUserRepository): self.usuarios = usuarios
    async def execute(self, usuario_id: int, sede_id: int) -> PermisosEfectivosResponse:
        u = await self.usuarios.get_by_id(usuario_id)
        perms = {p.nombre_completo for r in u.roles for p in r.permisos}
        return PermisosEfectivosResponse(usuario_id=usuario_id, sede_id=sede_id, permisos=sorted(perms))
