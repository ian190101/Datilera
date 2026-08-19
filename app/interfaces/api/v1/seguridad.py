# app/interfaces/api/v1/seguridad.py
from __future__ import annotations


from fastapi import APIRouter, Depends, status, Response, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, model_validator


from app.interfaces.api.v1.deps import (
    get_settings_dep,
    get_usuarios_repo,
    get_sesiones_repo,
    get_revocados_repo,
    get_hasher,
    get_tokens,
    get_roles_repo,
    get_usuarios_roles_repo,
    get_session,
)


from app.infrastructure.db.repositories.seguridad.sesiones_repo import SesionesRepository
from app.infrastructure.db.repositories.seguridad.tokens_revocados_repo import TokensRevocadosRepository


from app.kernel.application.seguridad.login import Login, LoginRequest, LoginResponse
from app.kernel.application.seguridad.refresh import Refresh, RefreshRequest, RefreshResponse
from app.kernel.application.seguridad.cerrar_sesion import CerrarSesion, CerrarSesionRequest
from app.kernel.application.seguridad.registrar_usuario import (
    RegistrarUsuario,
    RegistrarUsuarioRequest,
    RegistrarUsuarioResponse,
)
from app.infrastructure.db.repositories.seguridad.usuarios_repo import UsuariosRepository
from app.infrastructure.db.repositories.seguridad.roles_repo import RolesRepository
from app.infrastructure.db.repositories.seguridad.usuarios_roles_repo import UsuarioRolRepository
from app.infrastructure.auth.login_rate_limiter import login_rate_limiter


from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractHasher, AbstractTokenService
from app.middleware.api_auth import AuthPrincipal, get_current_principal, require_module_access
from app.infrastructure.db.models.seguridad.usuarios import Usuario as UsuarioModel


router = APIRouter(prefix="/auth", tags=["Seguridad"])


class CambiarPasswordObligatorioRequest(BaseModel):
    password_actual: str = Field(min_length=8, max_length=128)
    password_nueva: str = Field(min_length=12, max_length=128)
    password_confirmacion: str = Field(min_length=12, max_length=128)

    @model_validator(mode="after")
    def validar_passwords(self):
        if self.password_nueva != self.password_confirmacion:
            raise ValueError("Las contraseñas nuevas no coinciden")
        if self.password_actual == self.password_nueva:
            raise ValueError("La nueva contraseña debe ser diferente de la temporal")
        return self


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



# app/interfaces/api/v1/seguridad.py (o seguridad.py)
from app.infrastructure.db.uow import UnitOfWork
from app.interfaces.api.v1.deps import get_uow_dep

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    settings=Depends(get_settings_dep),
    uow: UnitOfWork = Depends(get_uow_dep),
    hasher: AbstractHasher = Depends(get_hasher),
    tokens: AbstractTokenService = Depends(get_tokens),
):
    session = uow.session_required

    usuarios_repo = UsuariosRepository(session)
    sesiones_repo = SesionesRepository(session)

    cu = Login(
        usuarios=usuarios_repo,
        hasher=hasher,
        tokens=tokens,
        sesiones=sesiones_repo,
        limiter=login_rate_limiter,
        refresh_ttl_min=int(settings.refresh_token_expire_days) * 24 * 60,
    )

    req = body.model_copy(
        update={
            "ip": request.client.host if request.client else "127.0.0.1",
            "user_agent": request.headers.get("user-agent", "unknown"),
        }
    )

    res = await cu.execute(req)
    # Cerrar transacción de login/sesión
    await uow.commit()

    secure_flag = settings.is_production
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

    # Si Login no hace commit interno y modifica BD:
    # await uow.commit()

    return res


@router.post("/cambiar-password-obligatorio")
async def cambiar_password_obligatorio(
    body: CambiarPasswordObligatorioRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session),
    hasher: AbstractHasher = Depends(get_hasher),
):
    usuario = await session.get(UsuarioModel, principal.usuario_id)
    if not usuario or not usuario.activo:
        raise HTTPException(status_code=401, detail="Usuario inexistente o inactivo")
    if not usuario.debe_cambiar_password:
        raise HTTPException(status_code=409, detail="La cuenta no requiere cambio obligatorio")
    if not hasher.verify_password(body.password_actual, usuario.hash_password):
        raise HTTPException(status_code=400, detail="La contraseña temporal es incorrecta")

    usuario.hash_password = hasher.hash_password(body.password_nueva)
    usuario.debe_cambiar_password = False
    usuario.password_temporal_generada_en = None
    await session.commit()
    return {"success": True, "mensaje": "Contraseña actualizada correctamente"}




@router.post("/refresh", response_model=RefreshResponse, status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(get_uow_dep),
    tokens: AbstractTokenService = Depends(get_tokens),
    settings=Depends(get_settings_dep),
):
    rt = request.cookies.get(REFRESH_COOKIE)
    if not rt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No hay refresh token")


    session = uow.session_required
    cu = Refresh(
        usuarios=UsuariosRepository(session),
        tokens=tokens,
        revocados=TokensRevocadosRepository(session),
        sesiones=SesionesRepository(session),
        refresh_expire_days=int(settings.refresh_token_expire_days),
    )
    ua = request.headers.get("user-agent")


    res = await cu.execute(
        RefreshRequest(
            refresh_token=rt,
            ip=request.client.host if request.client else None,
            user_agent=ua,
        )
    )
    await uow.commit()


    secure_flag = settings.is_production


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
    uow: UnitOfWork = Depends(get_uow_dep),
    tokens: AbstractTokenService = Depends(get_tokens),
):
    rt = request.cookies.get(REFRESH_COOKIE)


    clear_access_cookie(response)
    clear_refresh_cookie(response)


    if not rt:
        return


    session = uow.session_required
    cu = CerrarSesion(
        sesiones=SesionesRepository(session),
        tokens=tokens,
        revocados=TokensRevocadosRepository(session),
    )
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
    await uow.commit()
    return



@router.post("/register", response_model=RegistrarUsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegistrarUsuarioRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
    hasher=Depends(get_hasher),
    principal: AuthPrincipal = Depends(require_module_access("Usuarios", "Seguridad")),
):
    if body.sede_id != principal.sede_id and not principal.puede_acceder_modulo("Sedes", "Seguridad"):
        raise HTTPException(status_code=403, detail="No puede crear usuarios en otra sede")
    session = uow.session_required
    cu = RegistrarUsuario(
        usuarios=UsuariosRepository(session),
        roles=RolesRepository(session),
        usuarios_roles=UsuarioRolRepository(session),
        hasher=hasher,
    )
    result = await cu.execute(body)
    await uow.commit()
    return result
