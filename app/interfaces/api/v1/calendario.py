# app/interfaces/api/v1/calendario.py

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session

# Repositorios
from app.infrastructure.db.repositories.calendario import (
    TiposEventosRepository,
    EventosCalendarioRepository,
    PlanificacionActividadRepository,
)

# Casos de uso
from app.kernel.application.calendario import (
    # Tipos de Eventos
    CrearTipoEventoUseCase,
    ObtenerTipoEventoUseCase,
    ListarTiposEventosUseCase,
    ActualizarTipoEventoUseCase,
    ActivarTipoEventoUseCase,
    DesactivarTipoEventoUseCase,
    
    # Eventos
    CrearEventoUseCase,
    ObtenerEventoUseCase,
    ListarEventosUseCase,
    ListarEventosPorFechaUseCase,
    ListarEventosPorMesUseCase,
    ActualizarEventoUseCase,
    EliminarEventoUseCase,
    AprobarEventoUseCase,
    RechazarEventoUseCase,
    
    # Planificación
    CrearPlanificacionUseCase,
    ObtenerPlanificacionUseCase,
    ListarPlanificacionesPorFechaUseCase,
    ListarPlanificacionesPorRangoUseCase,
    ListarPlanificacionesProfesoraUseCase,
    ActualizarPlanificacionUseCase,
    EliminarPlanificacionUseCase,
    MarcarCompletadaUseCase,
    ObtenerPlanificacionesPendientesUseCase,
)

router = APIRouter(prefix="/calendario", tags=["Calendario y Planificación"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Helpers DI
def tipos_eventos_repo(db: AsyncSession) -> TiposEventosRepository:
    return TiposEventosRepository(db)

def eventos_repo(db: AsyncSession) -> EventosCalendarioRepository:
    return EventosCalendarioRepository(db)

def planificacion_repo(db: AsyncSession) -> PlanificacionActividadRepository:
    return PlanificacionActividadRepository(db)


# ===========================================================================
# TIPOS DE EVENTOS
# ===========================================================================

@router.post("/tipos-eventos", status_code=status.HTTP_201_CREATED)
async def crear_tipo_evento(
    db: SessionDep,
    # payload: CrearTipoEventoRequest,
):
    """Crear tipo de evento (directora/admin/superadmin)."""
    uc = CrearTipoEventoUseCase(tipos_eventos_repo(db))
    # return await uc.ejecutar(**payload.model_dump())
    raise HTTPException(status_code=501, detail="Creación de tipos de evento no disponible en esta API")


@router.get("/tipos-eventos/{tipo_id}")
async def obtener_tipo_evento(tipo_id: int, db: SessionDep):
    """Obtener tipo de evento por ID."""
    uc = ObtenerTipoEventoUseCase(tipos_eventos_repo(db))
    return await uc.ejecutar(tipo_id)


@router.get("/tipos-eventos")
async def listar_tipos_eventos(
    db: SessionDep,
    sede_id: int | None = None,
    activo: bool | None = None,
    solo_visibles_profesoras: bool = False,
    solo_visibles_tutores: bool = False,
):
    """Listar tipos de eventos con filtros."""
    uc = ListarTiposEventosUseCase(tipos_eventos_repo(db))
    return await uc.ejecutar(
        sede_id=sede_id,
        activo=activo,
        solo_visibles_profesoras=solo_visibles_profesoras,
        solo_visibles_tutores=solo_visibles_tutores,
    )


@router.put("/tipos-eventos/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_tipo_evento(
    tipo_id: int,
    db: SessionDep,
    # payload: ActualizarTipoEventoRequest,
):
    """Actualizar tipo de evento (directora/admin/superadmin)."""
    uc = ActualizarTipoEventoUseCase(tipos_eventos_repo(db))
    # await uc.ejecutar(tipo_id, **payload.model_dump(exclude_unset=True))
    return None


@router.patch("/tipos-eventos/{tipo_id}/activar", status_code=status.HTTP_204_NO_CONTENT)
async def activar_tipo_evento(tipo_id: int, db: SessionDep):
    """Activar tipo de evento."""
    uc = ActivarTipoEventoUseCase(tipos_eventos_repo(db))
    await uc.ejecutar(tipo_id)
    return None


@router.patch("/tipos-eventos/{tipo_id}/desactivar", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_tipo_evento(tipo_id: int, db: SessionDep):
    """Desactivar tipo de evento (si no tiene eventos asociados)."""
    uc = DesactivarTipoEventoUseCase(tipos_eventos_repo(db))
    await uc.ejecutar(tipo_id)
    return None


# ===========================================================================
# EVENTOS DEL CALENDARIO
# ===========================================================================

@router.post("/eventos", status_code=status.HTTP_201_CREATED)
async def crear_evento(
    db: SessionDep,
    # payload: CrearEventoRequest,
):
    """Crear evento (profesoras/directora/admin)."""
    uc = CrearEventoUseCase(eventos_repo(db), tipos_eventos_repo(db))
    # return await uc.ejecutar(**payload.model_dump())
    raise HTTPException(status_code=501, detail="Creación de eventos no disponible en esta API")


@router.get("/eventos/{evento_id}")
async def obtener_evento(evento_id: int, db: SessionDep):
    """Obtener evento por ID."""
    uc = ObtenerEventoUseCase(eventos_repo(db))
    return await uc.ejecutar(evento_id)


@router.get("/eventos")
async def listar_eventos(
    db: SessionDep,
    sede_id: int | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    tipo_evento_id: int | None = None,
    aprobado: bool | None = None,
    limite: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Listar eventos con filtros."""
    uc = ListarEventosUseCase(eventos_repo(db))
    return await uc.ejecutar(
        sede_id=sede_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo_evento_id=tipo_evento_id,
        aprobado=aprobado,
        limite=limite,
        offset=offset,
    )


@router.get("/eventos/fecha/{fecha}")
async def listar_eventos_por_fecha(
    fecha: date,
    db: SessionDep,
    sede_id: int | None = None,
    solo_aprobados: bool = True,
):
    """Listar eventos de una fecha específica."""
    uc = ListarEventosPorFechaUseCase(eventos_repo(db))
    return await uc.ejecutar(fecha, sede_id, solo_aprobados)


@router.get("/eventos/mes/{anio}/{mes}")
async def listar_eventos_por_mes(
    db: SessionDep,  # ✅ Primero (sin valor por defecto)
    anio: int = Path(..., ge=1900, le=2100),
    mes: int = Path(..., ge=1, le=12),
    sede_id: int | None = None,
    solo_aprobados: bool = True,
):
    """Listar eventos de un mes específico."""
    uc = ListarEventosPorMesUseCase(eventos_repo(db))
    return await uc.ejecutar(anio, mes, sede_id, solo_aprobados)



@router.put("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_evento(
    evento_id: int,
    db: SessionDep,
    # payload: ActualizarEventoRequest,
):
    """Actualizar evento (creador/directora/admin)."""
    uc = ActualizarEventoUseCase(eventos_repo(db))
    # await uc.ejecutar(evento_id, **payload.model_dump(exclude_unset=True))
    return None


@router.delete("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_evento(evento_id: int, db: SessionDep):
    """Eliminar evento (creador/directora/admin)."""
    uc = EliminarEventoUseCase(eventos_repo(db))
    await uc.ejecutar(evento_id)
    return None


@router.patch("/eventos/{evento_id}/aprobar", status_code=status.HTTP_204_NO_CONTENT)
async def aprobar_evento(
    evento_id: int,
    aprobado_por: int,  # TODO: Obtener de JWT
    db: SessionDep = None,
):
    """Aprobar evento pendiente (directora/admin)."""
    uc = AprobarEventoUseCase(eventos_repo(db))
    await uc.ejecutar(evento_id, aprobado_por)
    return None


@router.delete("/eventos/{evento_id}/rechazar", status_code=status.HTTP_204_NO_CONTENT)
async def rechazar_evento(evento_id: int, db: SessionDep):
    """Rechazar evento pendiente (directora/admin)."""
    uc = RechazarEventoUseCase(eventos_repo(db))
    await uc.ejecutar(evento_id)
    return None


# ===========================================================================
# PLANIFICACIÓN DE ACTIVIDADES
# ===========================================================================

@router.post("/planificacion", status_code=status.HTTP_201_CREATED)
async def crear_planificacion(
    db: SessionDep,
    # payload: CrearPlanificacionRequest,
):
    """Crear planificación de actividad (profesora)."""
    uc = CrearPlanificacionUseCase(planificacion_repo(db), eventos_repo(db))
    # return await uc.ejecutar(**payload.model_dump())
    raise HTTPException(status_code=501, detail="Creación de planificaciones disponible en el módulo Académico")


@router.get("/planificacion/{planificacion_id}")
async def obtener_planificacion(planificacion_id: int, db: SessionDep):
    """Obtener planificación por ID."""
    uc = ObtenerPlanificacionUseCase(planificacion_repo(db))
    return await uc.ejecutar(planificacion_id)


@router.get("/planificacion/fecha/{fecha}")
async def listar_planificaciones_por_fecha(
    fecha: date,
    db: SessionDep,
    sede_id: int | None = None,
    profesora_id: int | None = None,
    paralelo_id: int | None = None,
):
    """Listar planificaciones de una fecha específica."""
    uc = ListarPlanificacionesPorFechaUseCase(planificacion_repo(db))
    return await uc.ejecutar(fecha, sede_id, profesora_id, paralelo_id)


@router.get("/planificacion/rango")
async def listar_planificaciones_por_rango(
    fecha_inicio: date,
    fecha_fin: date,
    db: SessionDep,
    sede_id: int | None = None,
    profesora_id: int | None = None,
):
    """Listar planificaciones en un rango de fechas."""
    uc = ListarPlanificacionesPorRangoUseCase(planificacion_repo(db))
    return await uc.ejecutar(fecha_inicio, fecha_fin, sede_id, profesora_id)


@router.get("/planificacion/profesora/{profesora_id}")
async def listar_planificaciones_profesora(
    profesora_id: int,
    db: SessionDep,
    dias_adelante: int = Query(7, ge=1, le=30),
):
    """Listar planificaciones de una profesora (próximos N días)."""
    uc = ListarPlanificacionesProfesoraUseCase(planificacion_repo(db))
    return await uc.ejecutar(profesora_id, dias_adelante)


@router.put("/planificacion/{planificacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_planificacion(
    planificacion_id: int,
    db: SessionDep,
    # payload: ActualizarPlanificacionRequest,
):
    """Actualizar planificación (profesora responsable/directora)."""
    uc = ActualizarPlanificacionUseCase(planificacion_repo(db))
    # await uc.ejecutar(planificacion_id, **payload.model_dump(exclude_unset=True))
    return None


@router.delete("/planificacion/{planificacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_planificacion(
    planificacion_id: int,
    db: SessionDep,
    permitir_eliminar_completadas: bool = False,
):
    """Eliminar planificación (profesora responsable/directora)."""
    uc = EliminarPlanificacionUseCase(planificacion_repo(db))
    await uc.ejecutar(planificacion_id, permitir_eliminar_completadas)
    return None


@router.patch("/planificacion/{planificacion_id}/completar", status_code=status.HTTP_204_NO_CONTENT)
async def marcar_planificacion_completada(
    planificacion_id: int,
    db: SessionDep,
    # payload: MarcarCompletadaRequest,  # { notas_ejecucion?: str }
):
    """Marcar planificación como completada (profesora responsable)."""
    uc = MarcarCompletadaUseCase(planificacion_repo(db))
    # await uc.ejecutar(planificacion_id, payload.notas_ejecucion)
    await uc.ejecutar(planificacion_id, None)  # TODO: pasar notas
    return None


@router.get("/planificacion/pendientes")
async def obtener_planificaciones_pendientes(
    db: SessionDep,
    fecha_limite: date | None = None,
    sede_id: int | None = None,
    profesora_id: int | None = None,
):
    """Obtener planificaciones no completadas."""
    uc = ObtenerPlanificacionesPendientesUseCase(planificacion_repo(db))
    return await uc.ejecutar(fecha_limite, sede_id, profesora_id)
