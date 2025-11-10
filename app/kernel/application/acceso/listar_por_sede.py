#app/kernel/application/acceso/listar_por_sede.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field

from app.kernel.domain.acceso.codigo_acceso_entidad import CodigoAcceso
from app.kernel.domain.acceso.estado_codigo_entidad import EstadoCodigo
from app.kernel.domain.acceso.ports import UnitOfWork

class ListarCodigosPorSedeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sede_id: int
    estados: Optional[list[EstadoCodigo]] = None
    rol_destino: Optional[str] = None
    vigentes_en: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)

class ListarCodigosPorSedeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: Sequence[CodigoAcceso]
    total: int | None = None  # si luego añades count

class ListarCodigosPorSede:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def execute(self, req: ListarCodigosPorSedeRequest) -> ListarCodigosPorSedeResponse:
        async with self.uow:
            items = await self.uow.codigos.listar_por_sede(
                req.sede_id,
                estados=req.estados,
                rol_destino=req.rol_destino,
                vigentes_en=req.vigentes_en,
                limit=req.limit,
                offset=req.offset,
            )
        return ListarCodigosPorSedeResponse(items=items)
