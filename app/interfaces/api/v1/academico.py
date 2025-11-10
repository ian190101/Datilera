# app/interfaces/api/v1/academico.py
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.sql import expression as expr  # para collate si se requiere
from sqlalchemy.ext.asyncio import AsyncSession

from app.interfaces.api.v1.seguridad import get_current_user_id  # 401/403 delegados a seguridad
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.db.uow import UnitOfWork
from app.interfaces.api.deps import uow_dependency  # tu dependencia que abre UoW por request

# ⚠️ Ajusta esta ruta si tu modelo está en otro paquete/módulo
from app.infrastructure.db.models.academico import Grupo  # asumiendo existe Grupo(id, nombre, ...)

router = APIRouter(prefix="/academico", tags=["Académico"])

# Colación opcional (solo si quieres forzar insensibilidad para MySQL en el filtro LIKE)
# Ejemplos: "utf8mb4_general_ci", "utf8mb4_unicode_ci"
MYSQL_LIKE_COLLATE: Optional[str] = os.getenv("MYSQL_LIKE_COLLATE", "").strip() or None


@router.get("/grupos")
async def listar_grupos(
    q: Optional[str] = Query(default=None, description="Texto a buscar en el nombre del grupo"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="nombre", regex="^(id|nombre)$"),
    direction: str = Query(default="asc", regex="^(asc|desc)$"),
    _user_id: str = Depends(get_current_user_id),  # 401/403 lo maneja seguridad.py
    uow: UnitOfWork = Depends(uow_dependency),
) -> Dict[str, Any]:
    """
    Lista grupos con búsqueda, orden y paginación.

    Ajustes puntuales:
    - Búsqueda: se usa LIKE; la insensibilidad depende de la colación de tu BD.
      Para MySQL, puedes fijar MYSQL_LIKE_COLLATE=utf8mb4_general_ci si deseas forzarla aquí.
    - Orden y paginación: order_by aplicado ANTES de limit/offset.
    - 401/403: delegados a seguridad (get_current_user_id / require_roles).
    """
    session: AsyncSession = uow.session_required

    # Base query
    stmt = select(Grupo)

    # Filtro q (mínimo viable con LIKE)
    if q:
        pattern = f"%{q}%"
        if MYSQL_LIKE_COLLATE:
            # Forzar colación en el campo para MySQL si lo necesitas
            stmt = stmt.where(expr.collate(Grupo.nombre, MYSQL_LIKE_COLLATE).like(pattern))
        else:
            stmt = stmt.where(Grupo.nombre.like(pattern))

    # Conteo total (para paginación)
    count_stmt = select(func.count(Grupo.id))
    if q:
        if MYSQL_LIKE_COLLATE:
            count_stmt = count_stmt.where(expr.collate(Grupo.nombre, MYSQL_LIKE_COLLATE).like(pattern))
        else:
            count_stmt = count_stmt.where(Grupo.nombre.like(pattern))

    total = (await session.execute(count_stmt)).scalar_one()

    # Orden
    if sort == "nombre":
        order_col = Grupo.nombre
    else:
        order_col = Grupo.id

    if direction == "desc":
        order_col = order_col.desc()
    else:
        order_col = order_col.asc()

    # APLICAR order_by ANTES de limit/offset
    stmt = stmt.order_by(order_col)
    stmt = stmt.limit(limit).offset(offset)

    res = await session.execute(stmt)
    items = res.scalars().all()

    # Serialización mínima (ajusta campos según tu modelo)
    data: List[Dict[str, Any]] = [
        {
            "id": g.id,
            "nombre": getattr(g, "nombre", None),
        }
        for g in items
    ]

    return {
        "items": data,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "direction": direction,
        },
    }


@router.get("/grupos/{grupo_id}")
async def obtener_grupo(
    grupo_id: int,
    _user_id: str = Depends(get_current_user_id),  # 401/403 delegados a seguridad
    uow: UnitOfWork = Depends(uow_dependency),
) -> Dict[str, Any]:
    """Detalle de un grupo por id."""
    session: AsyncSession = uow.session_required
    g = await session.get(Grupo, grupo_id)
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")

    return {
        "id": g.id,
        "nombre": getattr(g, "nombre", None),
    }