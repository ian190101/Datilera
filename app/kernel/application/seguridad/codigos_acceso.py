# app/kernel/application/seguridad/codigos_acceso.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone
from typing import Protocol
from app.kernel.domain.acceso.errors import CodigoNoEncontrado, CodigoExpirado, CodigoAgotado, CodigoRevocado
from app.kernel.domain.acceso.codigo_acceso_entidad import CodigoAcceso

class ICodigosService(Protocol):
    async def validar_consumir(self, valor: str, usuario_id: int) -> CodigoAcceso: ...
    async def generar(self, sede_id: int, rol_id: int, alumno_id: int | None) -> CodigoAcceso: ...
    async def revocar(self, codigo_id: int, motivo: str | None = None) -> None: ...

class ValidarConsumirCodigoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    valor: str = Field(min_length=6, max_length=6)
    usuario_id: int

class GenerarCodigoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sede_id: int
    rol_id: int
    alumno_id: int | None = None

class RevocarCodigoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo_id: int
    motivo: str | None = None

class ValidarConsumirCodigo:
    def __init__(self, svc: ICodigosService): self.svc = svc
    async def execute(self, req: ValidarConsumirCodigoRequest) -> CodigoAcceso:
        return await self.svc.validar_consumir(req.valor, req.usuario_id)

class GenerarCodigo:
    def __init__(self, svc: ICodigosService): self.svc = svc
    async def execute(self, req: GenerarCodigoRequest) -> CodigoAcceso:
        return await self.svc.generar(req.sede_id, req.rol_id, req.alumno_id)

class RevocarCodigo:
    def __init__(self, svc: ICodigosService): self.svc = svc
    async def execute(self, req: RevocarCodigoRequest) -> None:
        await self.svc.revocar(req.codigo_id, req.motivo)
