# app/interfaces/api/v1/rol_permisos.py
from fastapi import APIRouter, Depends, Body
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.seguridad.roles_permiso_repo import RolPermisoRepository
from app.infrastructure.db.repositories.seguridad.roles_repo import RolesRepository
from app.infrastructure.db.repositories.seguridad.permisos_repo import PermisosRepository

from app.kernel.application.seguridad.rol_permiso.asignar_permiso_rol import (
    AsignarPermisoRol,
    AsignarPermisoRolDTO,
)
from app.kernel.application.seguridad.rol_permiso.cambiar_permiso_rol import (
    CambiarPermisoRol,
    CambiarPermisoRolDTO,
)
from app.kernel.application.seguridad.rol_permiso.revocar_permiso_rol import (
    RevocarPermisoRol,
    RevocarPermisoRolDTO,
)
from app.kernel.application.seguridad.rol_permiso.listar_permisos_rol import ListarPermisosRol

router = APIRouter(prefix="/seguridad/rol-permisos", tags=["Rol-Permisos"])


def get_rol_repo(session: AsyncSession = Depends(get_session)) -> RolesRepository:
    return RolesRepository(session)


def get_permiso_repo(session: AsyncSession = Depends(get_session)) -> PermisosRepository:
    return PermisosRepository(session)


def get_rol_permiso_repo(session: AsyncSession = Depends(get_session)) -> RolPermisoRepository:
    return RolPermisoRepository(session)


@router.post("/asignar", status_code=status.HTTP_201_CREATED)
async def asignar_permiso_rol(
    payload: AsignarPermisoRolDTO = Body(...),
    rol_repo: RolesRepository = Depends(get_rol_repo),
    permiso_repo: PermisosRepository = Depends(get_permiso_repo),
    rol_permiso_repo: RolPermisoRepository = Depends(get_rol_permiso_repo),
):
    """Asigna un permiso a un rol."""
    caso = AsignarPermisoRol(rol_repo, permiso_repo, rol_permiso_repo)
    await caso.execute(payload)
    return {"message": "Permiso asignado exitosamente al rol"}


@router.put("/cambiar")
async def cambiar_permiso_rol(
    payload: CambiarPermisoRolDTO = Body(...),
    rol_repo: RolesRepository = Depends(get_rol_repo),
    permiso_repo: PermisosRepository = Depends(get_permiso_repo),
    rol_permiso_repo: RolPermisoRepository = Depends(get_rol_permiso_repo),
):
    """Cambia el permiso de un rol (revoca el anterior y asigna el nuevo)."""
    caso = CambiarPermisoRol(rol_repo, permiso_repo, rol_permiso_repo)
    await caso.execute(payload)
    return {"message": "Permiso cambiado exitosamente"}


@router.delete("/revocar", status_code=status.HTTP_204_NO_CONTENT)
async def revocar_permiso_rol(
    payload: RevocarPermisoRolDTO = Body(...),
    rol_permiso_repo: RolPermisoRepository = Depends(get_rol_permiso_repo),
):
    """Revoca un permiso específico de un rol."""
    caso = RevocarPermisoRol(rol_permiso_repo)
    await caso.execute(payload)
    return


@router.get("/{rol_id}")
async def listar_permisos_rol(
    rol_id: int,
    rol_repo: RolesRepository = Depends(get_rol_repo),
    rol_permiso_repo: RolPermisoRepository = Depends(get_rol_permiso_repo),
):
    """Lista todos los permisos asignados a un rol."""
    caso = ListarPermisosRol(rol_repo, rol_permiso_repo)
    result = await caso.execute(rol_id)
    return result
