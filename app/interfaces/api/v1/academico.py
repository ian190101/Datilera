# app/interfaces/api/v1/academico.py
from __future__ import annotations
from datetime import time

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select
from typing import Annotated, Sequence

from app.infrastructure.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

# Repositorios
from app.infrastructure.db.repositories.academico.grupos_repo import GruposRepository
from app.infrastructure.db.repositories.academico.paralelos_repo import ParalelosRepository
from app.infrastructure.db.repositories.academico.paralelos_profesoras_repo import ParalelosProfesorasRepository
from app.infrastructure.db.repositories.academico.horarios_repo import HorariosRepository
from app.infrastructure.db.models.academico.horarios import Horario as HorarioModel


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


def grupo_repo(db: AsyncSession) -> GruposRepository: 
    return GruposRepository(db)

def paralelo_repo(db: AsyncSession) -> ParalelosRepository: 
    return ParalelosRepository(db)



def pp_repo(db: AsyncSession) -> ParalelosProfesorasRepository: 
    return ParalelosProfesorasRepository(db)


class HorarioPayload(BaseModel):
    nombre: str = Field(min_length=1, max_length=50)
    hora_inicio: time
    hora_fin: time

    @model_validator(mode="after")
    def validar_rango(self):
        self.nombre = self.nombre.strip()
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser menor que la hora de fin")
        return self


def _horario_response(horario: HorarioModel) -> dict:
    return {
        "id": horario.id,
        "nombre": horario.nombre,
        "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
        "hora_fin": horario.hora_fin.strftime("%H:%M"),
        "creado_en": horario.creado_en.isoformat() if horario.creado_en else None,
    }


# Horarios. Esta API modular es la fuente oficial para la pantalla académica.
@router.get("/horarios")
async def listar_horarios(
    db: SessionDep,
    search: str = Query("", max_length=50),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    filtros = []
    if search.strip():
        filtros.append(HorarioModel.nombre.ilike(f"%{search.strip()}%"))
    where = filtros[0] if filtros else None
    repo = HorariosRepository(db)
    items = await repo.list(where=where, limit=limit, offset=offset, order_by=HorarioModel.hora_inicio)
    total_stmt = select(func.count(HorarioModel.id))
    if where is not None:
        total_stmt = total_stmt.where(where)
    total = int((await db.execute(total_stmt)).scalar_one())
    return {"items": [_horario_response(item) for item in items], "total": total}


@router.get("/horarios/{horario_id}")
async def obtener_horario(horario_id: int, db: SessionDep):
    horario = await HorariosRepository(db).get(horario_id)
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    return _horario_response(horario)


@router.post("/horarios", status_code=status.HTTP_201_CREATED)
async def crear_horario(payload: HorarioPayload, db: SessionDep):
    repo = HorariosRepository(db)
    if await repo.exists_nombre_ci(nombre=payload.nombre):
        raise HTTPException(status_code=409, detail="Ya existe un horario con ese nombre")
    horario = HorarioModel(**payload.model_dump())
    await repo.create(horario)
    await db.commit()
    await db.refresh(horario)
    return _horario_response(horario)


@router.put("/horarios/{horario_id}")
async def actualizar_horario(horario_id: int, payload: HorarioPayload, db: SessionDep):
    repo = HorariosRepository(db)
    horario = await repo.get(horario_id)
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    if await repo.exists_nombre_ci(nombre=payload.nombre, excluir_id=horario_id):
        raise HTTPException(status_code=409, detail="Ya existe un horario con ese nombre")
    await repo.update(horario_id, payload.model_dump())
    await db.commit()
    horario = await repo.get(horario_id)
    return _horario_response(horario)





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
