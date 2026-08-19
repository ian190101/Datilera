# app/interfaces/api/v1/sedes/sedes.py
from fastapi import APIRouter, Depends, Query, Body
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.seguridad.sede_repo import SedeRepository

from app.kernel.application.seguridad.sede.crear_sede import CrearSede, CrearSedeDTO
from app.kernel.application.seguridad.sede.editar_sede import EditarSede, EditarSedeDTO
from app.kernel.application.seguridad.sede.obtener_sede import ObtenerSede
from app.kernel.application.seguridad.sede.desactivar_sede import EliminarSede
from app.kernel.application.seguridad.sede.listar_sedes import ListarSedes, ListarSedesDTO

router = APIRouter(prefix="/sedes", tags=["Sedes"])

def get_repo(session: AsyncSession = Depends(get_session)) -> SedeRepository:
    return SedeRepository(session)

@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_sede(
    payload: CrearSedeDTO = Body(...),
    repo: SedeRepository = Depends(get_repo),
):
    caso = CrearSede(repo)
    sede = await caso.execute(payload)
    return {"data": sede.model_dump()}

@router.put("/{sede_id}")
async def editar_sede(
    sede_id: int,
    payload: EditarSedeDTO = Body(...),
    repo: SedeRepository = Depends(get_repo),
):
    # asegurar que el dto use el path param
    payload_dict = payload.model_dump()
    payload_dict["sede_id"] = sede_id
    caso = EditarSede(repo)
    sede = await caso.execute(EditarSedeDTO(**payload_dict))
    return {"data": sede.model_dump()}

@router.get("/{sede_id}")
async def obtener_sede(
    sede_id: int,
    repo: SedeRepository = Depends(get_repo),
):
    caso = ObtenerSede(repo)
    sede = await caso.execute(sede_id)
    return {"data": sede.model_dump()}

@router.delete("/{sede_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_sede(
    sede_id: int,
    repo: SedeRepository = Depends(get_repo),
):
    caso = EliminarSede(repo)
    await caso.execute(sede_id)
    return

@router.get("")
async def listar_sedes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    activo: bool | None = Query(None),
    repo: SedeRepository = Depends(get_repo),
):
    caso = ListarSedes(repo)
    dto = ListarSedesDTO(page=page, per_page=per_page, activo=activo)
    result = await caso.execute(dto)
    return result
