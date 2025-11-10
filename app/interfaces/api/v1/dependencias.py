# app/interfaces/api/dependencias.py
from fastapi import Depends, HTTPException, status, Request
from typing import Annotated, Callable
from app.infrastructure.db.uow import get_uow, AsyncSessionLocal, UnitOfWork 
from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractHasher, AbstractTokenService
from app.kernel.domain.seguridad.permiso_entidad import Accion
from app.kernel.domain.common.excepciones import RBACDenegadoError, InvalidCredentialsError
from app.config.settings import get_settings
from app.infrastructure.auth.auth_utils import PyJWTTokenService, PasslibHasher
from app.infrastructure.db.repositories.seguridad.usuarios_repo import SQLAlchemyUsuariosRepository 
from app.infrastructure.db.repositories.auditoria.auditoria_acciones_repo import AuditoriaAccionesRepository
from typing import List

# ---------------------------------------------
# 1. Dependencias de Infraestructura (Adaptadores)
# ---------------------------------------------

settings = get_settings()

def get_hasher() -> AbstractHasher:
    """Provee el adaptador de hashing."""
    return PasslibHasher()

def get_token_service() -> AbstractTokenService:
    """Provee el adaptador de JWT."""
    return PyJWTTokenService()

# ---------------------------------------------
# 2. Dependencia UoW (Transaccional)
# ---------------------------------------------

# Adaptador de UoW: Aquí integramos el factory de sessiones con el UoW
def get_uow_dep() -> Callable[[Request], UnitOfWork]:
    """Retorna una función que provee el UnitOfWork con la sesión asíncrona."""
    # Nota: Usamos lambda o una función para que FastAPI pueda resolverlo
    return lambda: get_uow(AsyncSessionLocal)

UnitOfWorkDep = Annotated[UnitOfWork, Depends(get_uow_dep())]

# ---------------------------------------------
# 3. Dependencia de Autenticación/RBAC
# ---------------------------------------------

def get_current_user_id(request: Request, token_service: AbstractTokenService = Depends(get_token_service)) -> int:
    """
    Decodifica el Access Token del header Authorization.
    Retorna el ID de usuario si es válido, sino lanza 401.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado en el encabezado Authorization.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = token_service.decode_token(token)
        if payload.get("type") != "access":
            raise InvalidCredentialsError()
        return int(payload["sub"])
    except Exception: # Captura excepciones de JWT
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]

# ---------------------------------------------
# 4. Función de Chequeo de Permiso (HOC para Routers)
# ---------------------------------------------

def requiere_permiso(recurso: str, accion: Accion) -> Callable:
    """
    High-Order Component: Crea una dependencia que verifica el permiso.
    """
    def check_permission(request: Request, user_id: CurrentUserIdDep, uow: UnitOfWorkDep) -> None:
        """
        Dependencia que revisa si el token tiene el permiso requerido.
        Nota: Esto se puede optimizar cargando el usuario desde el UoW.
        """
        try:
            # Opción 1 (Rápida y basada en token): Revisa el payload del token (si el token es el Source of Truth)
            auth_header = request.headers.get("Authorization")
            token = auth_header.split(" ")[1]
            payload = get_token_service().decode_token(token)
            
            permisos: List[str] = payload.get("pms", [])
            permiso_requerido = f"{recurso}:{accion.value}"
            
            if permiso_requerido not in permisos:
                raise RBACDenegadoError(f"Requiere el permiso: {permiso_requerido}")
            
        except RBACDenegadoError:
            # Lanzamos el error de Dominio para que lo atrape el handler global
            raise
        except Exception:
            # Cualquier otro fallo de token/extracción debe ser 401
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error de autenticación al verificar permiso.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return Depends(check_permission)
