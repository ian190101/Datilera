# app/interfaces/api/v1/comunicaciones/notificaciones.py

from fastapi import APIRouter, Depends, Query, Body, Path
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.db.uow import get_uow, UnitOfWork
from typing import Dict, List
from datetime import datetime

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.comunicaciones.notificaciones_repo import NotificacionesRepository
from app.infrastructure.db.repositories.comunicaciones.notificacion_vistas_repo import NotificacionVistasRepository
from app.infrastructure.db.repositories.seguridad.usuarios_repo import UsuariosRepository
from app.kernel.application.comunicaciones.notificaciones import (
    CrearNotificacionUseCase,
    ObtenerNotificacionUseCase,
    ListarNotificacionesUseCase,
    MarcarNotificacionLeidaUseCase,
    MarcarTodasLeidasUseCase,
    ContarNoLeidasUseCase,
    CrearNotificacionProgramadaUseCase,
    CancelarNotificacionProgramadaUseCase,
    ListarTiposNotificacionesUseCase,
    AgruparNotificacionesPorTipoUseCase,  # NUEVO
    EnviarNotificacionMasivaUseCase,  # NUEVO
)

from app.kernel.application.comunicaciones.notificaciones.marcar_notificacion_leida_badge import (
    MarcarNotificacionLeidaConBadgeService,
)
from app.kernel.application.comunicaciones.notificaciones.marcar_todas_leidas_badge import (
    MarcarTodasLeidasConBadgeService,
)

from app.kernel.domain.comunicaciones import CanalNotificacion
from app.infrastructure.services.notificador_service_mock import NotificadorServiceMock

# TODO: Importar servicio cuando esté implementado
# from app.infrastructure.services.notificador_service import NotificadorService

router = APIRouter(prefix="/comunicaciones/notificaciones", tags=["Comunicaciones - Notificaciones"])


# ==========================================
# Dependencies
# ==========================================

def get_notificacion_repo(session: AsyncSession = Depends(get_session)) -> NotificacionesRepository:
    return NotificacionesRepository(session)

def get_usuario_repo(session: AsyncSession = Depends(get_session)) -> UsuariosRepository:
    return UsuariosRepository(session)


def get_vista_repo(session: AsyncSession = Depends(get_session)) -> NotificacionVistasRepository:
    return NotificacionVistasRepository(session)


# TODO: Implementar cuando esté disponible
# def get_notificador_service() -> NotificadorService:
#     return NotificadorService()


# ==========================================
# Endpoints
# ==========================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_notificacion(
    usuario_id: int = Body(...),
    titulo: str = Body(...),
    cuerpo: str = Body(...),
    tipo: str = Body(...),
    relacionado_tipo: str | None = Body(None),
    relacionado_id: int | None = Body(None),
    canal: CanalNotificacion = Body(CanalNotificacion.IN_APP),
    prioridad: str = Body("media"),
    programada_para: datetime | None = Body(None),
    metadatos: Dict | None = Body(None),
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
    # notificador_service: NotificadorService = Depends(get_notificador_service),
):
    """Crear notificación (US-COM-004).
    
    Body:
        - usuario_id: Usuario destinatario
        - titulo: Título (obligatorio, ≤120 chars)
        - cuerpo: Cuerpo (obligatorio)
        - tipo: Tipo de notificación
        - relacionado_tipo: Tipo de entidad relacionada (opcional)
        - relacionado_id: ID de entidad relacionada (opcional)
        - canal: Canal de envío (in_app, email, push, sms)
        - prioridad: Prioridad (baja, media, alta)
        - programada_para: Fecha/hora de envío programado (opcional)
        - metadatos: Datos adicionales (opcional)
    """
    # TODO: Inyectar notificador_service cuando esté implementado
    
    notificador_service = NotificadorServiceMock()
    
    caso = CrearNotificacionUseCase(notificacion_repo, notificador_service)
    notificacion = await caso.ejecutar(
        usuario_id=usuario_id,
        titulo=titulo,
        cuerpo=cuerpo,
        tipo=tipo,
        relacionado_tipo=relacionado_tipo,
        relacionado_id=relacionado_id,
        canal=canal,
        prioridad=prioridad,
        programada_para=programada_para,
        metadatos=metadatos,
    )
    
    return {"data": notificacion.model_dump()}


@router.get("/{notificacion_id}")
async def obtener_notificacion(
    notificacion_id: int = Path(...),
    usuario_id: int = Query(...),
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
    vista_repo: NotificacionVistasRepository = Depends(get_vista_repo),
):
    """Obtener detalle de notificación.
    
    Registra vista automáticamente.
    """
    caso = ObtenerNotificacionUseCase(notificacion_repo, vista_repo)
    notificacion = await caso.ejecutar(notificacion_id, usuario_id)
    
    return {"data": notificacion.model_dump()}


@router.get("")
async def listar_notificaciones(
    usuario_id: int = Query(...),
    tipo: str | None = Query(None),
    leidas: bool | None = Query(None),
    limite: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
):
    """Listar notificaciones del usuario (US-COM-008).
    
    Ordenadas por creado_en DESC.
    """
    caso = ListarNotificacionesUseCase(notificacion_repo)
    notificaciones = await caso.ejecutar(
        usuario_id=usuario_id,
        tipo=tipo,
        leidas=leidas,
        limite=limite,
        offset=offset,
    )
    
    return {
        "data": [n.model_dump() for n in notificaciones],
        "pagination": {
            "limite": limite,
            "offset": offset,
            "total": len(notificaciones),
        }
    }


@router.patch("/{notificacion_id}/leer", status_code=status.HTTP_204_NO_CONTENT)
async def marcar_notificacion_leida(
    notificacion_id: int = Path(...),
    usuario_id: int = Body(...),
    sede_id: int = Body(...),
    uow: UnitOfWork = Depends(lambda: get_uow(AsyncSessionLocal)),
):
    """Marcar notificación como leída (US-COM-008).

    Idempotente (no falla si ya está leída).
    """
    service = MarcarNotificacionLeidaConBadgeService(uow)
    await service.ejecutar(
        notificacion_id=notificacion_id,
        usuario_id=usuario_id,
        sede_id=sede_id,
    )
    return


@router.patch("/leer-todas", status_code=status.HTTP_200_OK)
async def marcar_todas_leidas(
    usuario_id: int = Body(...),
    sede_id: int = Body(...),
    uow: UnitOfWork = Depends(lambda: get_uow(AsyncSessionLocal)),
):
    service = MarcarTodasLeidasConBadgeService(uow)
    count = await service.ejecutar(usuario_id=usuario_id, sede_id=sede_id)
    return {"data": {"marcadas": count}}



@router.get("/no-leidas/contar")
async def contar_no_leidas(
    usuario_id: int = Query(...),
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
):
    """Contar notificaciones no leídas (US-COM-008).
    
    Para el badge/contador de la campanita.
    """
    caso = ContarNoLeidasUseCase(notificacion_repo)
    count = await caso.ejecutar(usuario_id)
    
    return {"data": {"no_leidas": count}}


@router.post("/programada", status_code=status.HTTP_201_CREATED)
async def crear_notificacion_programada(
    usuario_id: int = Body(...),
    titulo: str = Body(...),
    cuerpo: str = Body(...),
    tipo: str = Body(...),
    programada_para: datetime = Body(...),
    relacionado_tipo: str | None = Body(None),
    relacionado_id: int | None = Body(None),
    canal: CanalNotificacion = Body(CanalNotificacion.IN_APP),
    prioridad: str = Body("media"),
    metadatos: Dict | None = Body(None),
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
):
    """Crear notificación programada.
    
    Se envía en la fecha/hora indicada por un worker.
    """
    caso = CrearNotificacionProgramadaUseCase(notificacion_repo)
    notificacion = await caso.ejecutar(
        usuario_id=usuario_id,
        titulo=titulo,
        cuerpo=cuerpo,
        tipo=tipo,
        programada_para=programada_para,
        relacionado_tipo=relacionado_tipo,
        relacionado_id=relacionado_id,
        canal=canal,
        prioridad=prioridad,
        metadatos=metadatos,
    )
    
    return {"data": notificacion.model_dump()}


@router.delete("/programada/{notificacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancelar_notificacion_programada(
    notificacion_id: int = Path(...),
    usuario_id: int = Query(...),
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
):
    """Cancelar notificación programada.
    
    Solo se pueden cancelar notificaciones no enviadas.
    """
    caso = CancelarNotificacionProgramadaUseCase(notificacion_repo)
    await caso.ejecutar(notificacion_id, usuario_id)
    return


@router.get("/tipos/listar")
async def listar_tipos_notificaciones(
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
):
    """Listar tipos de notificaciones disponibles."""
    caso = ListarTiposNotificacionesUseCase(notificacion_repo)
    tipos = await caso.ejecutar()
    
    return {"data": tipos}
@router.get("/agrupar-por-tipo")
async def agrupar_notificaciones_por_tipo(
    usuario_id: int = Query(..., description="ID del usuario"),
    solo_no_leidas: bool = Query(False, description="Solo agrupar notificaciones no leídas"),
    limite_por_tipo: int = Query(50, ge=1, le=100, description="Máximo de notificaciones por tipo"),
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
):
    """Agrupar notificaciones por tipo (US-COM-008).
    
    Para organizar la campanita de notificaciones por categorías.
    
    Returns:
        {
            "notificaciones": {
                "pago_vencimiento": [...],
                "nuevo_mensaje": [...],
                "reporte_diario": [...]
            },
            "estadisticas": {
                "pago_vencimiento": 2,
                "nuevo_mensaje": 1,
                "reporte_diario": 5,
                "total": 8,
                "no_leidas": 3
            }
        }
    """
    caso = AgruparNotificacionesPorTipoUseCase(notificacion_repo)
    resultado = await caso.ejecutar(
        usuario_id=usuario_id,
        solo_no_leidas=solo_no_leidas,
        limite_por_tipo=limite_por_tipo
    )
    return {"data": resultado}


@router.post("/masivo", status_code=status.HTTP_202_ACCEPTED)
async def enviar_notificacion_masiva(
    emisor_id: int = Body(..., description="ID del usuario que envía (directora/admin/superadmin)"),
    titulo: str = Body(..., max_length=120, description="Título de la notificación"),
    cuerpo: str = Body(..., description="Cuerpo de la notificación"),
    tipo: str = Body(..., description="Tipo de notificación"),
    sede_ids: List[int] | None = Body(None, description="IDs de sedes (None = todas las sedes)"),
    rol_destinatarios: str | None = Body(None, description="Filtrar por rol: profesora, tutor, directora, etc."),
    canal: CanalNotificacion = Body(CanalNotificacion.IN_APP, description="Canal de envío"),
    prioridad: str = Body("media", description="Prioridad: baja, media, alta"),
    programada_para: datetime | None = Body(None, description="Programar envío (opcional)"),
    metadatos: Dict | None = Body(None, description="Metadatos adicionales"),
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
    usuario_repo: UsuariosRepository = Depends(get_usuario_repo),
):
    """Enviar notificación masiva (US-COM-009).
    
    Solo para directora, admin y superadmin.
    
    **Permisos:**
    - Superadmin: puede enviar a todas las sedes o filtrar por sede
    - Directora/Admin: solo a su sede
    
    **Filtros:**
    - Por sede(s): especificar lista de sede_ids o None para todas
    - Por rol: solo profesoras, solo tutores, etc.
    
    **Procesamiento:**
    - Si > 50 destinatarios: se encola en Celery/RQ para procesamiento asíncrono
    - Si ≤ 50 destinatarios: se crea inmediatamente
    
    Returns:
        {
            "notificaciones_creadas": 45,
            "destinatarios": [user_id1, user_id2, ...],
            "tarea_id": "uuid-tarea-celery" (si es asíncrono),
            "mensaje": "Notificación enviada/encolada..."
        }
    """
    notificador_service = NotificadorServiceMock()
    
    caso = EnviarNotificacionMasivaUseCase(
        notificacion_repo, 
        notificador_service,
        usuario_repo
    )
    
    resultado = await caso.ejecutar(
        emisor_id=emisor_id,
        titulo=titulo,
        cuerpo=cuerpo,
        tipo=tipo,
        sede_ids=sede_ids,
        rol_destinatarios=rol_destinatarios,
        canal=canal,
        prioridad=prioridad,
        programada_para=programada_para,
        metadatos=metadatos,
    )
    
    return {"data": resultado}

