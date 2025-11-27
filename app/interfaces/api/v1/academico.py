# app/interfaces/api/v1/academico.py
from __future__ import annotations
from fastapi import APIRouter, Depends, status, Query
from typing import Annotated, Sequence

from app.infrastructure.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

# Repositorios
from app.infrastructure.db.repositories.academico.grupos_repo import GruposRepository
from app.infrastructure.db.repositories.academico.paralelos_repo import ParalelosRepository
from app.infrastructure.db.repositories.academico.paralelos_profesoras_repo import ParalelosProfesorasRepository
from app.infrastructure.db.repositories.academico.horarios_repo import HorariosRepository
from app.infrastructure.db.repositories.academico.horarios_paralelos_repo import HorariosParalelosRepository

# Casos de uso
from app.kernel.application.academico.horarios.crear_horario import CrearHorario, CrearHorarioDTO, Horario
from app.kernel.application.academico.horarios.actualizar_horario import ActualizarHorario, ActualizarHorarioDTO
from app.kernel.application.academico.horarios.eliminar_horario import EliminarHorario
from app.kernel.application.academico.horarios.listar_horarios import ListarHorarios
from app.kernel.application.academico.horarios.obtener_horario import ObtenerHorario
from app.kernel.application.academico.grupos.crear_grupo import CrearGrupo, CrearGrupoDTO, Grupo
from app.kernel.application.academico.grupos.eliminar_grupo import EliminarGrupo
from app.kernel.application.academico.grupos.editar_grupo import EditarGrupo, EditarGrupoDTO
from app.kernel.application.academico.grupos.listar_grupo_por_sede import ListarGruposPorSede
from app.kernel.application.academico.grupos.obtener_grupo import ObtenerGrupo
from app.kernel.application.academico.paralelos.crear_paralelo import CrearParalelo, CrearParaleloDTO, Paralelo
from app.kernel.application.academico.paralelos.listar_paralelos_por_grupo import ListarParalelosPorGrupo
from app.kernel.application.academico.paralelos.obtener_paralelo import ObtenerParalelo
from app.kernel.application.academico.horarios_paralelos.asignar_horario_paralelo import (
    AsignarHorarioParalelo,
    AsignarHorarioParaleloDTO, HorarioParalelo
)
from app.kernel.application.academico.horarios_paralelos.listar_horarios_paralelos import ListarHorariosParalelos
from app.kernel.application.academico.paralelos_profesoras.asignar_paralelo_profesora import (
    AsignarProfesoraParalelo,
    AsignarProfesoraParaleloDTO, ParaleloProfesora
)
from app.kernel.application.academico.paralelos_profesoras.listar_paralelos_profesoras import ListarParalelosProfesoras

router = APIRouter(prefix="/academico", tags=["Académico"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Helpers para inyección de dependencias
def horario_repo(db: AsyncSession) -> HorariosRepository: 
    return HorariosRepository(db)

def grupo_repo(db: AsyncSession) -> GruposRepository: 
    return GruposRepository(db)

def paralelo_repo(db: AsyncSession) -> ParalelosRepository: 
    return ParalelosRepository(db)

def hp_repo(db: AsyncSession) -> HorariosParalelosRepository: 
    return HorariosParalelosRepository(db)

def pp_repo(db: AsyncSession) -> ParalelosProfesorasRepository: 
    return ParalelosProfesorasRepository(db)

# Horarios
@router.post("/horarios", response_model=Horario, status_code=status.HTTP_201_CREATED)
async def crear_horario(payload: CrearHorarioDTO, db: SessionDep):
    """Crea un nuevo horario."""
    uc = CrearHorario(horario_repo(db))
    return await uc.execute(payload)

@router.get("/horarios", response_model=Sequence[Horario])
async def listar_horarios(db: SessionDep):
    """Lista todos los horarios ordenados."""
    uc = ListarHorarios(horario_repo(db))
    return await uc.execute()

@router.get("/horarios/{horario_id}", response_model=Horario)
async def obtener_horario(horario_id: int, db: SessionDep):
    """Obtiene un horario por ID."""
    uc = ObtenerHorario(horario_repo(db))
    return await uc.execute(horario_id)

@router.put("/horarios/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_horario(horario_id: int, payload: ActualizarHorarioDTO, db: SessionDep):
    """Actualiza un horario existente."""
    uc = ActualizarHorario(horario_repo(db))
    await uc.execute(horario_id, payload)
    return None

@router.delete("/horarios/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_horario(horario_id: int, db: SessionDep):
    """Elimina un horario si no está en uso."""
    uc = EliminarHorario(horario_repo(db), hp_repo(db))
    await uc.execute(horario_id)
    return None

# Grupos
@router.post("/grupos", response_model=Grupo, status_code=status.HTTP_201_CREATED)
async def crear_grupo(payload: CrearGrupoDTO, db: SessionDep):
    """Crea un nuevo grupo en una sede."""
    from app.infrastructure.db.repositories.seguridad import SedesRepository
    uc = CrearGrupo(grupo_repo(db), SedesRepository(db))
    return await uc.execute(payload)

@router.get("/grupos", response_model=Sequence[Grupo])
async def listar_grupos(
    db: SessionDep,
    sede_id: int = Query(..., description="ID de la sede para filtrar"),
    gestion: int | None = Query(None, ge=2020, le=2100, description="Filtrar por gestión"),
    solo_activos: bool = Query(False, description="Solo grupos activos"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Lista grupos por sede con filtros opcionales."""
    uc = ListarGruposPorSede(grupo_repo(db))
    return await uc.execute(
        sede_id=sede_id, 
        gestion=gestion, 
        solo_activos=solo_activos, 
        limit=limit, 
        offset=offset
    )

@router.get("/grupos/{grupo_id}", response_model=Grupo)
async def obtener_grupo(grupo_id: int, db: SessionDep):
    """Obtiene un grupo por ID."""
    uc = ObtenerGrupo(grupo_repo(db))
    return await uc.execute(grupo_id)

@router.put("/grupos/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def editar_grupo(grupo_id: int, payload: EditarGrupoDTO, db: SessionDep):
    """Edita un grupo existente."""
    uc = EditarGrupo(grupo_repo(db))
    await uc.execute(grupo_id, payload)
    return None

@router.delete("/grupos/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_grupo(grupo_id: int, db: SessionDep):
    """Desactiva un grupo si no está en uso."""
    uc = EliminarGrupo(grupo_repo(db), paralelo_repo(db))
    await uc.execute(grupo_id)
    return None

# Paralelos
@router.post("/paralelos", response_model=Paralelo, status_code=status.HTTP_201_CREATED)
async def crear_paralelo(payload: CrearParaleloDTO, db: SessionDep):
    """Crea un nuevo paralelo en un grupo."""
    uc = CrearParalelo(paralelo_repo(db), grupo_repo(db))
    return await uc.execute(payload)

@router.get("/paralelos", response_model=Sequence[Paralelo])
async def listar_paralelos(
    db: SessionDep,
    grupo_id: int | None = Query(None, description="Filtrar por grupo"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Lista paralelos con filtro opcional por grupo."""
    uc = ListarParalelosPorGrupo(paralelo_repo(db))
    return await uc.execute(grupo_id=grupo_id, limit=limit, offset=offset)

@router.get("/paralelos/{paralelo_id}", response_model=Paralelo)
async def obtener_paralelo(paralelo_id: int, db: SessionDep):
    """Obtiene un paralelo por ID."""
    uc = ObtenerParalelo(paralelo_repo(db))
    return await uc.execute(paralelo_id)

# Horarios-Paralelos
@router.post("/horarios-paralelos", response_model=HorarioParalelo, status_code=status.HTTP_201_CREATED)
async def asignar_horario_paralelo(payload: AsignarHorarioParaleloDTO, db: SessionDep):
    """Asigna un horario a un paralelo."""
    uc = AsignarHorarioParalelo(hp_repo(db), paralelo_repo(db), horario_repo(db))
    return await uc.execute(payload)

@router.get("/horarios-paralelos", response_model=Sequence[HorarioParalelo])
async def listar_horarios_paralelos(
    db: SessionDep,
    paralelo_id: int | None = Query(None, description="Filtrar por paralelo"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Lista asignaciones de horarios a paralelos."""
    uc = ListarHorariosParalelos(hp_repo(db))
    return await uc.execute(paralelo_id=paralelo_id, limit=limit, offset=offset)

# Paralelos-Profesoras
@router.post("/paralelos-profesoras", response_model=ParaleloProfesora, status_code=status.HTTP_201_CREATED)
async def asignar_profesora_paralelo(payload: AsignarProfesoraParaleloDTO, db: SessionDep):
    """Asigna una profesora a un paralelo."""
    uc = AsignarProfesoraParalelo(pp_repo(db), paralelo_repo(db))
    return await uc.execute(payload)

@router.get("/paralelos-profesoras", response_model=Sequence[ParaleloProfesora])
async def listar_paralelos_profesoras(
    db: SessionDep,
    paralelo_id: int | None = Query(None, description="Filtrar por paralelo"),
    profesora_id: int | None = Query(None, description="Filtrar por profesora"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Lista asignaciones de profesoras a paralelos."""
    uc = ListarParalelosProfesoras(pp_repo(db))
    return await uc.execute(paralelo_id=paralelo_id, profesora_id=profesora_id, limit=limit, offset=offset)