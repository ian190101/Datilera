from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.infrastructure.auth.auth_utils import PyJWTTokenService
from app.infrastructure.db.models.seguridad.roles import Rol
from app.infrastructure.db.models.seguridad.usuarios import Usuario
from app.infrastructure.db.session import get_session


async def get_current_web_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> Usuario | None:
    token = request.cookies.get("accesstoken") or request.cookies.get("access_token")
    if not token:
        header = request.headers.get("Authorization", "")
        token = header[7:].strip() if header.startswith("Bearer ") else None
    if not token:
        return None

    try:
        payload = PyJWTTokenService().decode_token(token)
        if payload.get("type") != "access":
            return None
        result = await db.execute(
            select(Usuario)
            .options(
                joinedload(Usuario.roles).joinedload(Rol.permisos),
                joinedload(Usuario.sede),
            )
            .where(Usuario.id == int(payload["sub"]), Usuario.activo.is_(True))
        )
        user = result.unique().scalars().first()
        if user and user.sede_id == int(payload["sede"]):
            return user
    except Exception:
        return None
    return None


async def get_current_web_user(
    user: Usuario | None = Depends(get_current_web_user_optional),
) -> Usuario:
    if user is None:
        raise HTTPException(status_code=401, detail="Autenticación requerida")
    return user
