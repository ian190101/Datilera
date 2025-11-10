#app/kernel/application/acceso/obtener_por_valor.py
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from app.kernel.domain.acceso.codigo_acceso_entidad import CodigoAcceso
from app.kernel.domain.acceso.errors import CodigoNoEncontrado, CodigoInvalido
from app.kernel.domain.acceso.ports import UnitOfWork

class ObtenerCodigoPorValorRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    valor: str = Field(min_length=6, max_length=6)

class ObtenerCodigoPorValorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo: CodigoAcceso

class ObtenerCodigoPorValor:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, req: ObtenerCodigoPorValorRequest) -> ObtenerCodigoPorValorResponse:
        if not req.valor or len(req.valor) != 6:
            raise CodigoInvalido("Valor inválido")
        async with self.uow:
            c = await self.uow.codigos.obtener_por_valor(req.valor.upper())
        if not c:
            raise CodigoNoEncontrado()
        return ObtenerCodigoPorValorResponse(codigo=c)
