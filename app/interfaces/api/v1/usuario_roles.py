# app/interfaces/api/v1/usuario_roles.py
from fastapi import APIRouter, Depends, Body
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.seguridad.usuarios_roles_repo import UsuarioRolRepository
from app.infrastructure.db.repositories.seguridad.usuarios_repo import UsuariosRepository
from app.infrastructure.db.repositories.seguridad.roles_repo import RolesRepository

from app.kernel.application.seguridad.usuario_rol.asignar_rol_usuario import (
    AsignarRolUsuario,
    AsignarRolUsuarioDTO,
)
from app.kernel.application.seguridad.usuario_rol.cambiar_rol_usuario import (
    CambiarRolUsuario,
    CambiarRolUsuarioDTO,
)
from app.kernel.application.seguridad.usuario_rol.revocar_rol_usuario import (
    RevocarRolUsuario,
    RevocarRolUsuarioDTO,
)
from app.kernel.application.seguridad.usuario_rol.listar_roles_usuario import ListarRolesUsuario

router = APIRouter(prefix="/api/v1/seguridad/usuario-roles", tags=["Usuario-Roles"])


def get_usuario_repo(session: AsyncSession = Depends(get_session)) -> UsuariosRepository:
    return UsuariosRepository(session)


def get_rol_repo(session: AsyncSession = Depends(get_session)) -> RolesRepository:
    return RolesRepository(session)


def get_usuario_rol_repo(session: AsyncSession = Depends(get_session)) -> UsuarioRolRepository:
    return UsuarioRolRepository(session)


@router.post("/asignar", status_code=status.HTTP_201_CREATED)
async def asignar_rol_usuario(
    payload: AsignarRolUsuarioDTO = Body(...),
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
    rol_repo: RolesRepository = Depends(get_rol_repo),
    usuario_rol_repo: UsuarioRolRepository = Depends(get_usuario_rol_repo),
):
    """Asigna un rol a un usuario."""
    caso = AsignarRolUsuario(usuario_repo, rol_repo, usuario_rol_repo)
    await caso.execute(payload)
    return {"message": "Rol asignado exitosamente"}


@router.put("/cambiar")
async def cambiar_rol_usuario(
    payload: CambiarRolUsuarioDTO = Body(...),
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
    rol_repo: RolesRepository = Depends(get_rol_repo),
    usuario_rol_repo: UsuarioRolRepository = Depends(get_usuario_rol_repo),
):
    """Cambia el rol de un usuario (revoca el anterior y asigna el nuevo)."""
    caso = CambiarRolUsuario(usuario_repo, rol_repo, usuario_rol_repo)
    await caso.execute(payload)
    return {"message": "Rol cambiado exitosamente"}


@router.delete("/revocar", status_code=status.HTTP_204_NO_CONTENT)
async def revocar_rol_usuario(
    payload: RevocarRolUsuarioDTO = Body(...),
    usuario_rol_repo: UsuarioRolRepository = Depends(get_usuario_rol_repo),
):
    """Revoca un rol específico de un usuario."""
    caso = RevocarRolUsuario(usuario_rol_repo)
    await caso.execute(payload)
    return


@router.get("/{usuario_id}")
async def listar_roles_usuario(
    usuario_id: int,
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
    usuario_rol_repo: UsuarioRolRepository = Depends(get_usuario_rol_repo),
):
    """Lista todos los roles asignados a un usuario."""
    caso = ListarRolesUsuario(usuario_repo, usuario_rol_repo)
    result = await caso.execute(usuario_id)
    return result
