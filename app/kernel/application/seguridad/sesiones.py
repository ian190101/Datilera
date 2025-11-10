# app/kernel/application/seguridad/sesiones.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Sequence, Protocol
from pydantic import BaseModel, ConfigDict

class SesionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    refresh_token: str
    expira_en: datetime

class ISesionQuery(Protocol):
    async def listar_por_usuario(self, usuario_id: int) -> Sequence[SesionDTO]: ...
    async def eliminar_por_id(self, sesion_id: int) -> bool: ...
    async def eliminar_todas(self, usuario_id: int) -> int: ...

class ListarSesiones:
    def __init__(self, sesiones: ISesionQuery): self.sesiones = sesiones
    async def execute(self, usuario_id: int) -> list[SesionDTO]:
        return list(await self.sesiones.listar_por_usuario(usuario_id))

class RevocarSesion:
    def __init__(self, sesiones: ISesionQuery): self.sesiones = sesiones
    async def execute(self, sesion_id: int) -> bool:
        return await self.sesiones.eliminar_por_id(sesion_id)

class RevocarTodasSesiones:
    def __init__(self, sesiones: ISesionQuery): self.sesiones = sesiones
    async def execute(self, usuario_id: int) -> int:
        return await self.sesiones.eliminar_todas(usuario_id)
