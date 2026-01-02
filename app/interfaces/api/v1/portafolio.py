from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Body, Path, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# 1. Base de datos (Igual que en sedes.py)
from app.infrastructure.db.session import get_session

# 2. Repositorios Concretos (Infraestructura)
from app.infrastructure.db.repositories.portafolio.reportes_diarios_repo import ReportesDiariosRepository
from app.infrastructure.db.repositories.portafolio.reporte_lecturas_tutores_repo import ReporteLecturasTutoresRepository
from app.infrastructure.db.repositories.portafolio.actividades_repo import ActividadesRepository
from app.infrastructure.db.repositories.portafolio.actividad_media_repo import ActividadMediaRepository
from app.infrastructure.notificaciones.service import NotificacionesService

from app.infrastructure.services.jobqueue_service import JobQueueService
# 3. Casos de Uso (Application Layer)
from app.kernel.application.portafolio.reporte import (
    CrearReporteDiarioCU, CrearReporteDiarioIn, CrearReporteDiarioOut,
    EnviarReporteDiarioCU, EnviarReporteDiarioIn, EnviarReporteDiarioOut,
    ListarReportesAlumnoCU, ListarReportesAlumnoIn, ListarReportesAlumnoOut,
)
from app.kernel.application.portafolio.lectura import (
    ConfirmarLecturaReporteCU, ConfirmarLecturaReporteIn, ConfirmarLecturaReporteOut,
    ListarLecturasPorReporteCU, ListarLecturasPorReporteIn, ListarLecturasPorReporteOut,
)
from app.kernel.application.portafolio.actividad import (
    CrearActividadPortafolioCU, CrearActividadPortafolioIn, CrearActividadPortafolioOut,
    ListarActividadConMediaCU, ListarActividadConMediaIn, ListarActividadConMediaOut,
)
from app.kernel.application.portafolio.media import (
    SubirMediaActividadCU, SubirMediaActividadIn, SubirMediaActividadOut,
    RegistrarDescargaMediaCU, RegistrarDescargaMediaIn, RegistrarDescargaMediaOut,
)

# 4. Errores de Dominio
from app.kernel.domain.portafolio import MediaNoEncontradaError


router = APIRouter(prefix="/api/v1/portafolio", tags=["Portafolio"])


# --------- PROVEEDORES DE DEPENDENCIAS (LOCALES) ---------
# Esto elimina la necesidad de usar deps.py, igual que en tu sedes.py

def get_reportes_repo(session: AsyncSession = Depends(get_session)) -> ReportesDiariosRepository:
    return ReportesDiariosRepository(session)

def get_lecturas_repo(session: AsyncSession = Depends(get_session)) -> ReporteLecturasTutoresRepository:
    return ReporteLecturasTutoresRepository(session)

def get_actividades_repo(session: AsyncSession = Depends(get_session)) -> ActividadesRepository:
    return ActividadesRepository(session)

def get_media_repo(session: AsyncSession = Depends(get_session)) -> ActividadMediaRepository:
    return ActividadMediaRepository(session)

def get_notificaciones_service(session: AsyncSession = Depends(get_session)) -> NotificacionesService:
    return NotificacionesService(session)


# --------- ENDPOINTS: REPORTES DIARIOS ---------

@router.post("/reportes", response_model=CrearReporteDiarioOut, status_code=status.HTTP_201_CREATED)
async def crear_reporte_diario(
    payload: CrearReporteDiarioIn = Body(...),
    repo: ReportesDiariosRepository = Depends(get_reportes_repo),
):
    caso = CrearReporteDiarioCU(repo)
    return await caso.execute(payload)


@router.post("/reportes/{reporte_id}/enviar", response_model=EnviarReporteDiarioOut)
async def enviar_reporte_diario(
    reporte_id: int = Path(..., gt=0),
    tutor_ids: List[int] = Body(..., embed=True),
    repo: ReportesDiariosRepository = Depends(get_reportes_repo),
    notifs: NotificacionesService = Depends(get_notificaciones_service),
):
    # Armamos el request combinando path param y body
    req = EnviarReporteDiarioIn(reporte_id=reporte_id, tutor_ids=tutor_ids)
    caso = EnviarReporteDiarioCU(repo, notifs)
    return await caso.execute(req)


@router.get("/alumnos/{alumno_id}/reportes", response_model=ListarReportesAlumnoOut)
async def listar_reportes_alumno(
    alumno_id: int = Path(..., gt=0),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None),
    repo: ReportesDiariosRepository = Depends(get_reportes_repo),
):
    req = ListarReportesAlumnoIn(alumno_id=alumno_id, desde=desde, hasta=hasta)
    caso = ListarReportesAlumnoCU(repo)
    return await caso.execute(req)


# --------- ENDPOINTS: LECTURAS DE TUTORES ---------

@router.post("/reportes/{reporte_id}/lecturas", response_model=ConfirmarLecturaReporteOut, status_code=status.HTTP_201_CREATED)
async def confirmar_lectura_reporte(
    reporte_id: int = Path(..., gt=0),
    tutor_id: int = Body(..., embed=True, gt=0),
    reportes_repo: ReportesDiariosRepository = Depends(get_reportes_repo),
    lecturas_repo: ReporteLecturasTutoresRepository = Depends(get_lecturas_repo),
):
    req = ConfirmarLecturaReporteIn(reporte_id=reporte_id, tutor_id=tutor_id)
    caso = ConfirmarLecturaReporteCU(reportes_repo, lecturas_repo)
    return await caso.execute(req)


@router.get("/reportes/{reporte_id}/lecturas", response_model=ListarLecturasPorReporteOut)
async def listar_lecturas_por_reporte(
    reporte_id: int = Path(..., gt=0),
    lecturas_repo: ReporteLecturasTutoresRepository = Depends(get_lecturas_repo),
):
    req = ListarLecturasPorReporteIn(reporte_id=reporte_id)
    caso = ListarLecturasPorReporteCU(lecturas_repo)
    return await caso.execute(req)


# --------- ENDPOINTS: ACTIVIDADES + MEDIA ---------

@router.post("/actividades", response_model=CrearActividadPortafolioOut, status_code=status.HTTP_201_CREATED)
async def crear_actividad_portafolio(
    payload: CrearActividadPortafolioIn = Body(...),
    actividades_repo: ActividadesRepository = Depends(get_actividades_repo),
):
    caso = CrearActividadPortafolioCU(actividades_repo)
    return await caso.execute(payload)


@router.get("/actividades/{actividad_id}", response_model=ListarActividadConMediaOut)
async def obtener_actividad_con_media(
    actividad_id: int = Path(..., gt=0),
    actividades_repo: ActividadesRepository = Depends(get_actividades_repo),
    media_repo: ActividadMediaRepository = Depends(get_media_repo),
):
    req = ListarActividadConMediaIn(actividad_id=actividad_id)
    caso = ListarActividadConMediaCU(actividades_repo, media_repo)
    return await caso.execute(req)



@router.post(
    "/actividades/{actividad_id}/media",
    response_model=SubirMediaActividadOut,
    status_code=status.HTTP_201_CREATED,
)
async def subir_media_actividad(
    actividad_id: int = Path(..., gt=0),
    payload: SubirMediaActividadIn = Body(...),
    actividades_repo: ActividadesRepository = Depends(get_actividades_repo),
    media_repo: ActividadMediaRepository = Depends(get_media_repo),
):
    # 1) Normalizar datos de entrada (la URL/ruta del archivo YA debe venir resuelta aquí)
    req = payload.model_copy(update={"actividad_id": actividad_id})

    # 2) Ejecutar caso de uso (solo persiste metadatos y ruta en BD)
    caso = SubirMediaActividadCU(actividades_repo, media_repo)
    out = await caso(req)

    # 3) Encolar procesamiento de marca de agua
    jobs = JobQueueService()
    jobs.enqueue_watermark_media(out.media.id)

    return out


@router.post("/media/{media_id}/descarga", response_model=RegistrarDescargaMediaOut)
async def registrar_descarga_media(
    media_id: int = Path(..., gt=0),
    media_repo: ActividadMediaRepository = Depends(get_media_repo),
):
    req = RegistrarDescargaMediaIn(media_id=media_id)
    caso = RegistrarDescargaMediaCU(media_repo)
    
    try:
        return await caso.execute(req)
    except MediaNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))