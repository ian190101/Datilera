# app/interfaces/api/v1/seguridad.py
from __future__ import annotations

from fastapi import APIRouter, Depends, status, Response, HTTPException, Request
from pydantic import BaseModel

from app.interfaces.api.v1.deps import (
    get_settings_dep,
    get_usuarios_repo,
    get_sesiones_repo,
    get_revocados_repo,
    get_hasher,
    get_tokens,
    get_auditoria_repo,
    get_roles_repo,                 
    get_usuarios_roles_repo,        
)

# Casos de uso (aplicación)
from app.kernel.application.seguridad.login import Login, LoginRequest, LoginResponse
from app.kernel.application.seguridad.refresh import Refresh, RefreshRequest, RefreshResponse
from app.kernel.application.seguridad.cerrar_sesion import CerrarSesion, CerrarSesionRequest
from app.kernel.application.seguridad.registrar_usuario import RegistrarUsuario, RegistrarUsuarioRequest, RegistrarUsuarioResponse


# Puertos
from app.kernel.domain.seguridad.ports import (
    AbstractUserRepository,
    AbstractHasher,
    AbstractTokenService,
)
from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort


router = APIRouter(prefix="/auth", tags=["Seguridad"])

REFRESH_COOKIE = "refresh_token"

def set_refresh_cookie(resp: Response, token: str, *, secure: bool, max_age: int) -> None:
    resp.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/api/v1/auth/refresh",
        max_age=max_age,
    )

def clear_refresh_cookie(resp: Response) -> None:
    resp.delete_cookie(key=REFRESH_COOKIE, path="/api/v1/auth/refresh")


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    settings = Depends(get_settings_dep),
    usuarios: AbstractUserRepository = Depends(get_usuarios_repo),
    hasher: AbstractHasher = Depends(get_hasher),
    tokens: AbstractTokenService = Depends(get_tokens),
    sesiones = Depends(get_sesiones_repo),
    auditoria: AuditoriaAccionRepositoryPort = Depends(get_auditoria_repo),
):
    limiter = type("NoopLimiter", (), {"check": staticmethod(lambda *_: None), "hit": staticmethod(lambda *_: None), "reset": staticmethod(lambda *_: None)})()
    cu = Login(usuarios=usuarios, hasher=hasher, tokens=tokens, sesiones=sesiones, limiter=limiter, auditoria=auditoria)
    ua = request.headers.get("user-agent")
    req = LoginRequest(username=body.username, password=body.password, ip=request.client.host if request.client else None, user_agent=ua)
    res = await cu.execute(req)
    set_refresh_cookie(response, res.refresh_token, secure=settings.API_SECRET_KEY != "INSECURE_SECRET", max_age=settings.REFRESH_TOKEN_EXPIRY_MINUTES * 60)
    return res


@router.post("/refresh", response_model=RefreshResponse, status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    response: Response,
    usuarios: AbstractUserRepository = Depends(get_usuarios_repo),
    tokens: AbstractTokenService = Depends(get_tokens),
    revocados = Depends(get_revocados_repo),
    auditoria: AuditoriaAccionRepositoryPort = Depends(get_auditoria_repo),
    settings = Depends(get_settings_dep),
):
    rt = request.cookies.get(REFRESH_COOKIE)
    if not rt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No hay refresh token")
    cu = Refresh(usuarios=usuarios, tokens=tokens, revocados=revocados, auditoria=auditoria)
    ua = request.headers.get("user-agent")
    res = await cu.execute(RefreshRequest(refresh_token=rt, ip=request.client.host if request.client else None, user_agent=ua))
    set_refresh_cookie(response, res.refresh_token, secure=settings.API_SECRET_KEY != "INSECURE_SECRET", max_age=settings.REFRESH_TOKEN_EXPIRY_MINUTES * 60)
    return res


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    sesiones = Depends(get_sesiones_repo),
    tokens: AbstractTokenService = Depends(get_tokens),
    revocados = Depends(get_revocados_repo),
    auditoria: AuditoriaAccionRepositoryPort = Depends(get_auditoria_repo),
):
    rt = request.cookies.get(REFRESH_COOKIE)
    clear_refresh_cookie(response)
    if not rt:
        return
    cu = CerrarSesion(sesiones=sesiones, tokens=tokens, revocados=revocados, auditoria=auditoria)
    ua = request.headers.get("user-agent")
    await cu.execute(CerrarSesionRequest(refresh_token=rt, ip=request.client.host if request.client else None, user_agent=ua, usuario_id=None, sede_id=None))
@router.post("/register", response_model=RegistrarUsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegistrarUsuarioRequest,
    usuarios = Depends(get_usuarios_repo),
    roles = Depends(get_roles_repo),
    usuarios_roles = Depends(get_usuarios_roles_repo),
    hasher = Depends(get_hasher),
):
    cu = RegistrarUsuario(usuarios=usuarios, roles=roles, usuarios_roles=usuarios_roles, hasher=hasher)
    return await cu.execute(body)