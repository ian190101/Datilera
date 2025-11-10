#app/kernel/application/acceso/disponible_codigo.py
from __future__ import annotations

from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from app.kernel.domain.acceso.estado_codigo_entidad import EstadoCodigo
from app.kernel.domain.acceso.ports import UnitOfWork

class DisponibilidadCodigoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    valor: str = Field(min_length=6, max_length=6)

class DisponibilidadCodigoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    valor: str
    disponible: bool

class DisponibilidadCodigo:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, req: DisponibilidadCodigoRequest) -> DisponibilidadCodigoResponse:
        async with self.uow:
            c = await self.uow.codigos.obtener_por_valor(req.valor.upper())
        if not c:
            return DisponibilidadCodigoResponse(valor=req.valor.upper(), disponible=False)
        if c.estado in (EstadoCodigo.expirado, EstadoCodigo.revocado):
            return DisponibilidadCodigoResponse(valor=req.valor.upper(), disponible=False)
        if c.expira_en and c.expira_en < date.today():
            return DisponibilidadCodigoResponse(valor=req.valor.upper(), disponible=False)
        return DisponibilidadCodigoResponse(valor=req.valor.upper(), disponible=c.cuentas_creadas < c.max_cuentas)

