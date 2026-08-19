from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.infrastructure.auth.auth_utils import PasslibHasher
from app.infrastructure.db.models.seguridad.preferencias_usuario import PreferenciaUsuario
from app.infrastructure.db.models.seguridad.sesiones import Sesion
from app.infrastructure.db.models.seguridad.usuarios import Usuario
from app.infrastructure.db.session import get_session
from app.infrastructure.services.secure_storage import SecureStorageService
from app.interfaces.web.auth import get_current_web_user
from app.main import templates


router = APIRouter(tags=["Perfil"])
storage = SecureStorageService(get_settings().MEDIA_DIR)
hasher = PasslibHasher()


class PasswordChangeRequest(BaseModel):
    password_actual: str = Field(min_length=8, max_length=128)
    password_nueva: str = Field(min_length=12, max_length=128)


class UserPreferencesRequest(BaseModel):
    theme: Literal["dark", "light"]


@router.get("/perfil", response_class=HTMLResponse)
async def profile_page(request: Request, user: Usuario = Depends(get_current_web_user)):
    return templates.TemplateResponse(
        "/usuarios/perfil.html",
        {"request": request, "current_user": user, "page_title": "Mi Perfil"},
    )


@router.post("/api/v1/perfil/foto")
async def update_profile_photo(
    file: UploadFile = File(...),
    user: Usuario = Depends(get_current_web_user),
    db: AsyncSession = Depends(get_session),
):
    stored = await storage.save_upload(
        file,
        "perfiles",
        allowed_mime_types={"image/jpeg", "image/png", "image/webp"},
        max_bytes=5 * 1024 * 1024,
    )
    user.foto_perfil_url = stored.public_url
    await db.commit()
    return {"success": True, "foto_url": stored.public_url}


@router.post("/api/v1/perfil/password")
async def update_profile_password(
    payload: PasswordChangeRequest,
    response: Response,
    user: Usuario = Depends(get_current_web_user),
    db: AsyncSession = Depends(get_session),
):
    if not hasher.verify_password(payload.password_actual, user.hash_password):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
    if payload.password_actual == payload.password_nueva:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe ser diferente")

    user.hash_password = hasher.hash_password(payload.password_nueva)
    user.debe_cambiar_password = False
    user.password_temporal_generada_en = None
    await db.execute(delete(Sesion).where(Sesion.usuario_id == user.id))
    await db.commit()
    response.delete_cookie("accesstoken", path="/")
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    return {"success": True, "mensaje": "Contraseña actualizada; vuelva a iniciar sesión"}


@router.patch("/api/v1/usuarios/me/preferencias")
async def update_preferences(
    prefs: UserPreferencesRequest,
    user: Usuario = Depends(get_current_web_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(PreferenciaUsuario).where(PreferenciaUsuario.usuario_id == user.id)
    )
    current = result.scalars().first()
    theme = "claro" if prefs.theme == "light" else "oscuro"
    if current:
        current.tema = theme
    else:
        db.add(PreferenciaUsuario(
            usuario_id=user.id,
            tema=theme,
            notificaciones_push=True,
            notificaciones_email=False,
        ))
    await db.commit()
    return {"status": "ok", "theme": prefs.theme}
