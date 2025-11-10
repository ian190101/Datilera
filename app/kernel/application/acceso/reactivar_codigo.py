#app/kernel/application/acceso/reactivar_codigo.py
from __future__ import annotations
from typing import Optional

from pydantic import BaseModel, ConfigDict
from app.kernel.domain.acceso.errors import CodigoNoEncontrado
from app.kernel.domain.acceso.ports import UnitOfWork

class ReactivarCodigoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo_id: int

class ReactivarCodigo:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, req: ReactivarCodigoRequest) -> None:
        async with self.uow:
            cod = await self.uow.codigos.obtener(req.codigo_id)
            if not cod:
                raise CodigoNoEncontrado()
            await self.uow.codigos.reactivar(req.codigo_id)
            await self.uow.commit()
