# app/interfaces/api/v1/roles.py
from fastapi import APIRouter, Depends, Query, Body
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.seguridad.roles_repo import RolesRepository

from app.kernel.application.seguridad.rol.crear_rol import CrearRol, CrearRolDTO
from app.kernel.application.seguridad.rol.editar_rol import EditarRol, EditarRolDTO
from app.kernel.application.seguridad.rol.obtener_rol import ObtenerRol
from app.kernel.application.seguridad.rol.desactivar_rol import DesactivarRol
from app.kernel.application.seguridad.rol.listar_roles import ListarRoles, ListarRolesDTO

router = APIRouter(prefix="/seguridad/roles", tags=["Roles"])


def get_repo(session: AsyncSession = Depends(get_session)) -> RolesRepository:
    return RolesRepository(session)


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_rol(
    payload: CrearRolDTO = Body(...),
    repo: RolesRepository = Depends(get_repo),
):
    caso = CrearRol(repo)
    rol = await caso.execute(payload)
    return {"data": rol.model_dump()}


@router.put("/{rol_id}")
async def editar_rol(
    rol_id: int,
    payload: EditarRolDTO = Body(...),
    repo: RolesRepository = Depends(get_repo),
):
    payload_dict = payload.model_dump()
    payload_dict["rol_id"] = rol_id
    caso = EditarRol(repo)
    rol = await caso.execute(EditarRolDTO(**payload_dict))
    return {"data": rol.model_dump()}


@router.get("/{rol_id}")
async def obtener_rol(
    rol_id: int,
    repo: RolesRepository = Depends(get_repo),
):
    caso = ObtenerRol(repo)
    rol = await caso.execute(rol_id)
    return {"data": rol.model_dump()}


@router.delete("/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_rol(
    rol_id: int,
    repo: RolesRepository = Depends(get_repo),
):
    caso = DesactivarRol(repo)
    await caso.execute(rol_id)
    return


@router.get("")
async def listar_roles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    activo: bool | None = Query(None),
    q: str | None = Query(None, max_length=50),
    repo: RolesRepository = Depends(get_repo),
):
    caso = ListarRoles(repo)
    dto = ListarRolesDTO(page=page, per_page=per_page, activo=activo, q=q)
    result = await caso.execute(dto)
    return result
