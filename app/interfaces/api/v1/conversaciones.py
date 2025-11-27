# app/interfaces/api/v1/comunicaciones/conversaciones.py

from fastapi import APIRouter, Depends, Query, Body, Path
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.comunicaciones.conversaciones_repo import ConversacionesRepository
from app.infrastructure.db.repositories.comunicaciones.conversaciones_participantes_repo import ConversacionesParticipantesRepository

from app.kernel.application.comunicaciones.conversaciones import (
    CrearConversacionUseCase,
    ObtenerConversacionUseCase,
    ListarConversacionesUseCase,
    CerrarConversacionUseCase,
    ReabrirConversacionUseCase,
    AgregarParticipanteUseCase,
    RemoverParticipanteUseCase,
    BuscarConversacionesUseCase,
)

from app.kernel.domain.comunicaciones import Participante, TipoConversacion

router = APIRouter(prefix="/api/v1/comunicaciones/conversaciones", tags=["Comunicaciones - Conversaciones"])


# ==========================================
# Dependencies
# ==========================================

def get_conversacion_repo(session: AsyncSession = Depends(get_session)) -> ConversacionesRepository:
    return ConversacionesRepository(session)


def get_participante_repo(session: AsyncSession = Depends(get_session)) -> ConversacionesParticipantesRepository:
    return ConversacionesParticipantesRepository(session)


# ==========================================
# Endpoints
# ==========================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def crear_conversacion(
    sede_id: int = Body(...),
    asunto: str = Body(...),
    creado_por_id: int = Body(...),
    participantes: List[dict] = Body(...),  # [{"usuario_id": int, "rol": str, "sede_id": int}]
    titulo: str | None = Body(None),
    descripcion: str | None = Body(None),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
):
    """Crear una conversación (US-COM-001).
    
    Body:
        - sede_id: ID de la sede
        - asunto: Asunto de la conversación (obligatorio, ≤120 chars)
        - creado_por_id: Usuario que crea
        - participantes: Lista de participantes (≥2)
        - titulo: Título opcional
        - descripcion: Descripción opcional
    """
    # Convertir dicts a Participante
    participantes_obj = [Participante(**p) for p in participantes]
    
    caso = CrearConversacionUseCase(conversacion_repo, participante_repo)
    conversacion = await caso.ejecutar(
        sede_id=sede_id,
        asunto=asunto,
        creado_por_id=creado_por_id,
        participantes=participantes_obj,
        titulo=titulo,
        descripcion=descripcion,
    )
    
    return {"data": conversacion.model_dump()}


@router.get("/{conversacion_id}")
async def obtener_conversacion(
    conversacion_id: int = Path(...),
    usuario_id: int = Query(...),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
):
    """Obtener detalle de conversación.
    
    Solo participantes pueden ver.
    """
    caso = ObtenerConversacionUseCase(conversacion_repo, participante_repo)
    conversacion = await caso.ejecutar(conversacion_id, usuario_id)
    
    return {"data": conversacion.model_dump()}


@router.get("")
async def listar_conversaciones(
    usuario_id: int = Query(...),
    sede_id: int | None = Query(None),
    cerradas: bool | None = Query(None),
    limite: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
):
    """Listar conversaciones del usuario (US-COM-007).
    
    Ordenadas por ultima_actividad_en DESC.
    """
    caso = ListarConversacionesUseCase(conversacion_repo)
    conversaciones = await caso.ejecutar(
        usuario_id=usuario_id,
        sede_id=sede_id,
        cerradas=cerradas,
        limite=limite,
        offset=offset,
    )
    
    return {
        "data": [c.model_dump() for c in conversaciones],
        "pagination": {
            "limite": limite,
            "offset": offset,
            "total": len(conversaciones),
        }
    }


@router.post("/{conversacion_id}/cerrar", status_code=status.HTTP_204_NO_CONTENT)
async def cerrar_conversacion(
    conversacion_id: int = Path(...),
    usuario_id: int = Body(...),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
):
    """Cerrar conversación (US-COM-006).
    
    Solo participantes pueden cerrar.
    """
    caso = CerrarConversacionUseCase(conversacion_repo, participante_repo)
    await caso.ejecutar(conversacion_id, usuario_id)
    return


@router.post("/{conversacion_id}/reabrir", status_code=status.HTTP_204_NO_CONTENT)
async def reabrir_conversacion(
    conversacion_id: int = Path(...),
    usuario_id: int = Body(...),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
):
    """Reabrir conversación cerrada."""
    caso = ReabrirConversacionUseCase(conversacion_repo, participante_repo)
    await caso.ejecutar(conversacion_id, usuario_id)
    return


@router.post("/{conversacion_id}/participantes", status_code=status.HTTP_201_CREATED)
async def agregar_participante(
    conversacion_id: int = Path(...),
    usuario_solicitante_id: int = Body(...),
    nuevo_participante: dict = Body(...),  # {"usuario_id": int, "rol": str, "sede_id": int}
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
):
    """Agregar participante a conversación."""
    participante_obj = Participante(**nuevo_participante)
    
    caso = AgregarParticipanteUseCase(conversacion_repo, participante_repo)
    await caso.ejecutar(conversacion_id, usuario_solicitante_id, participante_obj)
    
    return {"message": "Participante agregado exitosamente"}


@router.delete("/{conversacion_id}/participantes/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_participante(
    conversacion_id: int = Path(...),
    usuario_id: int = Path(...),
    usuario_solicitante_id: int = Query(...),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
):
    """Remover participante de conversación."""
    caso = RemoverParticipanteUseCase(conversacion_repo, participante_repo)
    await caso.ejecutar(conversacion_id, usuario_solicitante_id, usuario_id)
    return


@router.get("/buscar")
async def buscar_conversaciones(
    usuario_id: int = Query(...),
    termino: str = Query(..., min_length=1),
    limite: int = Query(20, ge=1, le=100),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
):
    """Buscar conversaciones por asunto."""
    caso = BuscarConversacionesUseCase(conversacion_repo)
    conversaciones = await caso.ejecutar(usuario_id, termino, limite)
    
    return {"data": [c.model_dump() for c in conversaciones]}
