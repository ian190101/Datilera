# app/kernel/application/sede/listar_sedes.py
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.ports import AbstractSedeRepository
from app.kernel.domain.seguridad.sede_entidad import Sede as SedeDomain

class ListarSedesDTO(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    activo: Optional[bool] = None

class ListarSedes:
    def __init__(self, sede_repo: AbstractSedeRepository):
        self.sede_repo = sede_repo

    async def execute(self, dto: ListarSedesDTO) -> dict[str, Any]:
        items, total = await self.sede_repo.list_paginated(
            page=dto.page,
            per_page=dto.per_page,
            activo=dto.activo,
        )
        return {
            "items": [SedeDomain.model_validate(i).model_dump() for i in items],
            "total": total,
            "page": dto.page,
            "per_page": dto.per_page,
        }
