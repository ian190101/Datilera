
from fastapi import APIRouter, Depends, HTTPException, status

from app.interfaces.api.v1.deps import get_uow_dep
from app.kernel.application.alumnos.crear_alumno import (
    CreateAlumno,
    CreateAlumnoRequest,
    AlumnoResponse,
)
from app.kernel.domain.exceptions import DuplicatedEntityException
from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.db.repositories.alumnos.alumnos import AlumnoRepository

router = APIRouter(prefix="/alumnos", tags=["Alumnos"])

@router.post("/", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
async def create_alumno(
    request: CreateAlumnoRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Registra un nuevo alumno en el sistema.
    """
    try:
        repository = AlumnoRepository(uow.session_required)
        service = CreateAlumno(repository)
        created_alumno = await service.execute(request)
        return created_alumno
    except DuplicatedEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
