# app/interfaces/api/v1/permisos.py
from fastapi import APIRouter, Depends, Query, Body
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.seguridad.permisos_repo import PermisosRepository

from app.kernel.application.seguridad.permiso.crear_permiso import CrearPermiso, CrearPermisoDTO
from app.kernel.application.seguridad.permiso.editar_permiso import EditarPermiso, EditarPermisoDTO
from app.kernel.application.seguridad.permiso.obtener_permiso import ObtenerPermiso
from app.kernel.application.seguridad.permiso.eliminar_permiso import EliminarPermiso
from app.kernel.application.seguridad.permiso.listar_permisos import ListarPermisos, ListarPermisosDTO

router = APIRouter(prefix="/seguridad/permisos", tags=["Permisos"])


def get_repo(session: AsyncSession = Depends(get_session)) -> PermisosRepository:
    return PermisosRepository(session)


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_permiso(
    payload: CrearPermisoDTO = Body(...),
    repo: PermisosRepository = Depends(get_repo),
):
    caso = CrearPermiso(repo)
    permiso = await caso.execute(payload)
    return {"data": permiso.model_dump()}


@router.put("/{permiso_id}")
async def editar_permiso(
    permiso_id: int,
    payload: EditarPermisoDTO = Body(...),
    repo: PermisosRepository = Depends(get_repo),
):
    payload_dict = payload.model_dump()
    payload_dict["permiso_id"] = permiso_id
    caso = EditarPermiso(repo)
    permiso = await caso.execute(EditarPermisoDTO(**payload_dict))
    return {"data": permiso.model_dump()}


@router.get("/{permiso_id}")
async def obtener_permiso(
    permiso_id: int,
    repo: PermisosRepository = Depends(get_repo),
):
    caso = ObtenerPermiso(repo)
    permiso = await caso.execute(permiso_id)
    return {"data": permiso.model_dump()}


@router.delete("/{permiso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_permiso(
    permiso_id: int,
    repo: PermisosRepository = Depends(get_repo),
):
    caso = EliminarPermiso(repo)
    await caso.execute(permiso_id)
    return


@router.get("")
async def listar_permisos(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    activo: bool | None = Query(None),
    q: str | None = Query(None, max_length=50),
    repo: PermisosRepository = Depends(get_repo),
):
    caso = ListarPermisos(repo)
    dto = ListarPermisosDTO(page=page, per_page=per_page, activo=activo, q=q)
    result = await caso.execute(dto)
    return result
