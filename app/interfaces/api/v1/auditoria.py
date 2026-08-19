from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.auditoria.auditoria_acciones_repo import AuditoriaAccionesRepository
from app.infrastructure.db.session import get_session
from app.middleware.api_auth import AuthPrincipal, require_module_access


router = APIRouter(prefix="/auditoria", tags=["Auditoría"])
AuditAccess = Depends(require_module_access("Auditoria", "Seguridad"))


def _serialize(model) -> dict[str, Any]:
    return {
        column.name: getattr(model, column.name)
        for column in model.__table__.columns
    }


@router.get("/acciones", dependencies=[AuditAccess])
async def listar_acciones(
    desde: datetime | None = None,
    hasta: datetime | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    principal: AuthPrincipal = Depends(require_module_access("Auditoria", "Seguridad")),
):
    records = await AuditoriaAccionesRepository(session).listar_por_sede(
        principal.sede_id,
        desde=desde,
        hasta=hasta,
        limit=limit,
        offset=offset,
    )
    return {"items": [_serialize(item) for item in records], "limit": limit, "offset": offset}


@router.get("/errores", dependencies=[AuditAccess])
async def listar_errores(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    principal: AuthPrincipal = Depends(require_module_access("Auditoria", "Seguridad")),
):
    records = await AuditoriaAccionesRepository(session).listar_errores(
        sede_id=principal.sede_id,
        limit=limit,
        offset=offset,
    )
    return {"items": [_serialize(item) for item in records], "limit": limit, "offset": offset}


@router.get("/estadisticas", dependencies=[AuditAccess])
async def estadisticas(
    desde: datetime | None = None,
    hasta: datetime | None = None,
    session: AsyncSession = Depends(get_session),
    principal: AuthPrincipal = Depends(require_module_access("Auditoria", "Seguridad")),
):
    repo = AuditoriaAccionesRepository(session)
    return {
        "por_accion": await repo.contar_por_accion(sede_id=principal.sede_id, desde=desde, hasta=hasta),
        "por_entidad": await repo.contar_por_entidad(sede_id=principal.sede_id, desde=desde, hasta=hasta),
        "usuarios_mas_activos": await repo.obtener_usuarios_mas_activos(
            sede_id=principal.sede_id, desde=desde, hasta=hasta, limit=10
        ),
    }
