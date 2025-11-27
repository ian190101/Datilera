# app/kernel/application/seguridad/roles/listar_roles.py
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.ports import AbstractRolRepository
from app.kernel.domain.seguridad.rol_entidad import Rol


class ListarRolesDTO(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    activo: Optional[bool] = None
    q: Optional[str] = Field(default=None, max_length=50)


class ListarRoles:
    """Caso de uso: Listar roles paginados."""
    def __init__(self, rol_repo: AbstractRolRepository):
        self.rol_repo = rol_repo

    async def execute(self, dto: ListarRolesDTO) -> dict[str, Any]:
        items, total = await self.rol_repo.list_paginated(
            page=dto.page,
            per_page=dto.per_page,
            activo=dto.activo,
            q=(dto.q.strip() if isinstance(dto.q, str) and dto.q.strip() else None),
        )
        return {
            "items": [r.model_dump() for r in items],
            "total": total,
            "page": dto.page,
            "per_page": dto.per_page,
        }
