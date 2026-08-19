# app/interfaces/api/v1/comunicaciones/estadisticas.py

from fastapi import APIRouter, Depends, Query
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.comunicaciones.conversaciones_repo import ConversacionesRepository
from app.infrastructure.db.repositories.comunicaciones.mensajes_repo import MensajesRepository
from app.infrastructure.db.repositories.comunicaciones.notificaciones_repo import NotificacionesRepository

from app.kernel.application.comunicaciones.estadisticas import (
    ObtenerEstadisticasUsuarioUseCase,
    ObtenerEstadisticasSedeUseCase,
)

router = APIRouter(prefix="/comunicaciones/estadisticas", tags=["Comunicaciones - Estadísticas"])


# ==========================================
# Dependencies
# ==========================================

def get_conversacion_repo(session: AsyncSession = Depends(get_session)) -> ConversacionesRepository:
    return ConversacionesRepository(session)


def get_mensaje_repo(session: AsyncSession = Depends(get_session)) -> MensajesRepository:
    return MensajesRepository(session)


def get_notificacion_repo(session: AsyncSession = Depends(get_session)) -> NotificacionesRepository:
    return NotificacionesRepository(session)


# ==========================================
# Endpoints
# ==========================================

@router.get("/usuario/{usuario_id}")
async def obtener_estadisticas_usuario(
    usuario_id: int,
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
    notificacion_repo: NotificacionesRepository = Depends(get_notificacion_repo),
):
    """Obtener estadísticas de comunicaciones del usuario.
    
    Incluye:
    - Total de conversaciones (abiertas/cerradas)
    - Total de mensajes (enviados/recibidos)
    - Total de notificaciones (leídas/no leídas)
    - Agrupación de notificaciones por tipo
    """
    caso = ObtenerEstadisticasUsuarioUseCase(
        conversacion_repo,
        mensaje_repo,
        notificacion_repo,
    )
    
    estadisticas = await caso.ejecutar(usuario_id)
    
    return {"data": estadisticas}


@router.get("/sede/{sede_id}")
async def obtener_estadisticas_sede(
    sede_id: int,
    usuarios_ids: List[int] = Query(...),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
):
    """Obtener estadísticas de comunicaciones por sede.
    
    Requiere lista de IDs de usuarios de la sede.
    Útil para reportes administrativos y dashboards.
    """
    caso = ObtenerEstadisticasSedeUseCase(conversacion_repo, mensaje_repo)
    estadisticas = await caso.ejecutar(sede_id, usuarios_ids)
    
    return {"data": estadisticas}
