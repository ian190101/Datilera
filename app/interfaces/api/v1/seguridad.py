# app/interfaces/api/v1/seguridad.py
from __future__ import annotations

from fastapi import APIRouter, Depends, status, Response, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

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
    get_session,
)

from app.infrastructure.db.repositories.seguridad.sesiones_repo import SesionesRepository

from app.kernel.application.seguridad.login import Login, LoginRequest, LoginResponse
from app.kernel.application.seguridad.refresh import Refresh, RefreshRequest, RefreshResponse
from app.kernel.application.seguridad.cerrar_sesion import CerrarSesion, CerrarSesionRequest
from app.kernel.application.seguridad.registrar_usuario import (
    RegistrarUsuario,
    RegistrarUsuarioRequest,
    RegistrarUsuarioResponse,
)

from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractHasher, AbstractTokenService
from app.kernel.domain.auditoria.ports import AuditoriaAccionRepositoryPort

router = APIRouter(prefix="/auth", tags=["Seguridad"])

ACCESS_COOKIE = "accesstoken"       # coincide con routes.py web [file:21]
REFRESH_COOKIE = "refresh_token"    # cookie refresh


def set_access_cookie(resp: Response, token: str, *, secure: bool, max_age: int) -> None:
    resp.set_cookie(
        key=ACCESS_COOKIE,
        value=token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
        max_age=max_age,
    )


def clear_access_cookie(resp: Response) -> None:
    resp.delete_cookie(key=ACCESS_COOKIE, path="/")


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
    settings=Depends(get_settings_dep),
    session: AsyncSession = Depends(get_session),
    usuarios: AbstractUserRepository = Depends(get_usuarios_repo),
    hasher: AbstractHasher = Depends(get_hasher),
    tokens: AbstractTokenService = Depends(get_tokens),
    auditoria: AuditoriaAccionRepositoryPort = Depends(get_auditoria_repo),
):
    class FakeLimiter:
        async def check(self, key): return None
        async def hit(self, key): pass
        async def reset(self, key): pass

    sesiones_repo = SesionesRepository(session)

    cu = Login(
        usuarios=usuarios,
        hasher=hasher,
        tokens=tokens,
        sesiones=sesiones_repo,
        limiter=FakeLimiter(),
        auditoria=auditoria,
    )

    req = body.model_copy(update={
        "ip": request.client.host if request.client else "127.0.0.1",
        "user_agent": request.headers.get("user-agent", "unknown"),
    })

    res = await cu.execute(req)

    secure_flag = settings.jwt_secret != "INSECURE_SECRET"

    # .env: ACCESS_EXPIRE_MIN=10, REFRESH_EXPIRE_DAYS=14
    set_access_cookie(
        response,
        res.access_token,  # ojo: es "accesstoken" [file:10]
        secure=secure_flag,
        max_age=int(settings.jwt_exp_minutes) * 60,
    )
    set_refresh_cookie(
        response,
        res.refresh_token,  # ojo: es "refreshtoken" [file:10]
        secure=secure_flag,
        max_age=int(settings.refresh_token_expire_days) * 24 * 60 * 60,
    )
    return res


@router.post("/refresh", response_model=RefreshResponse, status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    response: Response,
    usuarios: AbstractUserRepository = Depends(get_usuarios_repo),
    tokens: AbstractTokenService = Depends(get_tokens),
    revocados=Depends(get_revocados_repo),
    auditoria: AuditoriaAccionRepositoryPort = Depends(get_auditoria_repo),
    settings=Depends(get_settings_dep),
):
    rt = request.cookies.get(REFRESH_COOKIE)
    if not rt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No hay refresh token")

    cu = Refresh(usuarios=usuarios, tokens=tokens, revocados=revocados, auditoria=auditoria)
    ua = request.headers.get("user-agent")

    res = await cu.execute(
        RefreshRequest(
            refresh_token=rt,
            ip=request.client.host if request.client else None,
            user_agent=ua,
        )
    )

    secure_flag = settings.jwt_secret != "INSECURE_SECRET"

    # rotación: refresca ambos
    set_access_cookie(
        response,
        res.access_token,
        secure=secure_flag,
        max_age=int(settings.jwt_exp_minutes) * 60,
    )
    set_refresh_cookie(
        response,
        res.refresh_token,
        secure=secure_flag,
        max_age=int(settings.refresh_token_expire_days) * 24 * 60 * 60,
    )
    return res


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    sesiones=Depends(get_sesiones_repo),
    tokens: AbstractTokenService = Depends(get_tokens),
    revocados=Depends(get_revocados_repo),
    auditoria: AuditoriaAccionRepositoryPort = Depends(get_auditoria_repo),
):
    rt = request.cookies.get(REFRESH_COOKIE)

    clear_access_cookie(response)
    clear_refresh_cookie(response)

    if not rt:
        return

    cu = CerrarSesion(sesiones=sesiones, tokens=tokens, revocados=revocados, auditoria=auditoria)
    ua = request.headers.get("user-agent")

    await cu.execute(
        CerrarSesionRequest(
            refresh_token=rt,
            ip=request.client.host if request.client else None,
            user_agent=ua,
            usuario_id=None,
            sede_id=None,
        )
    )
    return


@router.post("/register", response_model=RegistrarUsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegistrarUsuarioRequest,
    usuarios=Depends(get_usuarios_repo),
    roles=Depends(get_roles_repo),
    usuarios_roles=Depends(get_usuarios_roles_repo),
    hasher=Depends(get_hasher),
):
    cu = RegistrarUsuario(usuarios=usuarios, roles=roles, usuarios_roles=usuarios_roles, hasher=hasher)
    return await cu.execute(body)
