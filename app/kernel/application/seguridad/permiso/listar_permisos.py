# app/kernel/application/seguridad/permisos/listar_permisos.py
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.ports import AbstractPermisoRepository


class ListarPermisosDTO(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    activo: Optional[bool] = None
    q: Optional[str] = Field(default=None, max_length=50)


class ListarPermisos:
    """Caso de uso: Listar permisos paginados."""
    def __init__(self, permiso_repo: AbstractPermisoRepository):
        self.permiso_repo = permiso_repo

    async def execute(self, dto: ListarPermisosDTO) -> dict[str, Any]:
        items, total = await self.permiso_repo.list_paginated(
            page=dto.page,
            per_page=dto.per_page,
            activo=dto.activo,
            q=(dto.q.strip() if isinstance(dto.q, str) and dto.q.strip() else None),
        )
        return {
            "items": [p.model_dump() for p in items],
            "total": total,
            "page": dto.page,
            "per_page": dto.per_page,
        }
