# app/kernel/application/seguridad/usuarios/listar_usuarios.py
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.kernel.domain.seguridad.ports import AbstractUserRepository


class ListarUsuariosDTO(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sede_id: Optional[int] = Field(None, gt=0)
    rol_nombre: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None
    q: Optional[str] = Field(None, max_length=100)


class ListarUsuarios:
    """Caso de uso: Listar usuarios con filtros."""

    def __init__(self, usuario_repo: AbstractUserRepository):
        self.usuario_repo = usuario_repo

    async def execute(self, dto: ListarUsuariosDTO) -> dict[str, Any]:
        items, total = await self.usuario_repo.list_paginated(
            page=dto.page,
            per_page=dto.per_page,
            sede_id=dto.sede_id,
            rol_nombre=dto.rol_nombre.strip().upper() if dto.rol_nombre else None,
            activo=dto.activo,
            q=dto.q.strip() if isinstance(dto.q, str) and dto.q.strip() else None,
        )
        return {
            "items": [
                {
                    "id": u.id,
                    "username": u.nombre_usuario,
                    "nombre_completo": getattr(u, "nombre_completo", ""),
                    "rol": u.rol.nombre,
                    "sede_id": u.sede_id,
                    "activo": u.activo,
                }
                for u in items
            ],
            "total": total,
            "page": dto.page,
            "per_page": dto.per_page,
        }
