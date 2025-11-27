# app/interfaces/api/v1/comunicaciones/mensajes.py

from fastapi import APIRouter, Depends, Query, Body, Path, UploadFile, File
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.comunicaciones.conversaciones_repo import ConversacionesRepository
from app.infrastructure.db.repositories.comunicaciones.conversaciones_participantes_repo import ConversacionesParticipantesRepository
from app.infrastructure.db.repositories.comunicaciones.mensajes_repo import MensajesRepository
from app.infrastructure.db.repositories.comunicaciones.mensajes_lectura_repo import MensajesLecturasRepository
from app.infrastructure.db.repositories.comunicaciones.mensajes_adjuntos_repo import MensajesAdjuntosRepository

from app.kernel.application.comunicaciones.mensajes import (
    EnviarMensajeUseCase,
    ObtenerMensajeUseCase,
    ListarMensajesUseCase,
    MarcarMensajeLeidoUseCase,
    ContarNoLeidosUseCase,
    BuscarMensajesUseCase,
    SubirAdjuntoUseCase,
    ListarAdjuntosUseCase,
    EliminarAdjuntoUseCase,
)

from app.kernel.domain.comunicaciones import TipoMensaje, TipoAdjunto
from app.infrastructure.services.storage_service_mock import StorageServiceMock
from app.infrastructure.services.websocket_service_mock import WebSocketServiceMock
# TODO: Importar servicios externos cuando estén implementados
# from app.infrastructure.services.websocket_service import WebSocketService
# from app.infrastructure.services.storage_service import StorageService

router = APIRouter(prefix="/api/v1/comunicaciones/mensajes", tags=["Comunicaciones - Mensajes"])


# ==========================================
# Dependencies
# ==========================================

def get_conversacion_repo(session: AsyncSession = Depends(get_session)) -> ConversacionesRepository:
    return ConversacionesRepository(session)


def get_participante_repo(session: AsyncSession = Depends(get_session)) -> ConversacionesParticipantesRepository:
    return ConversacionesParticipantesRepository(session)


def get_mensaje_repo(session: AsyncSession = Depends(get_session)) -> MensajesRepository:
    return MensajesRepository(session)


def get_lectura_repo(session: AsyncSession = Depends(get_session)) -> MensajesLecturasRepository:
    return MensajesLecturasRepository(session)


def get_adjunto_repo(session: AsyncSession = Depends(get_session)) -> MensajesAdjuntosRepository:
    return MensajesAdjuntosRepository(session)


# TODO: Implementar cuando esté disponible
# def get_websocket_service() -> WebSocketService:
#     return WebSocketService()

# def get_storage_service() -> StorageService:
#     return StorageService()


# ==========================================
# Endpoints
# ==========================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def enviar_mensaje(
    conversacion_id: int = Body(...),
    remitente_id: int = Body(...),
    contenido: str = Body(...),
    tipo: TipoMensaje = Body(TipoMensaje.TEXTO),
    reply_a_id: int | None = Body(None),
    metadatos: Dict | None = Body(None),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
    # websocket_service: WebSocketService = Depends(get_websocket_service),
):
    """Enviar mensaje en conversación (US-COM-002).
    
    Body:
        - conversacion_id: ID de la conversación
        - remitente_id: Usuario que envía
        - contenido: Contenido del mensaje (obligatorio, ≤4000 chars)
        - tipo: Tipo de mensaje (texto/sistema)
        - reply_a_id: ID del mensaje al que responde (opcional)
        - metadatos: Datos adicionales (opcional)
    """
    # TODO: Inyectar websocket_service cuando esté implementado
    
    websocket_service = WebSocketServiceMock()
    
    caso = EnviarMensajeUseCase(
        conversacion_repo,
        participante_repo,
        mensaje_repo,
        websocket_service,
    )
    
    mensaje = await caso.ejecutar(
        conversacion_id=conversacion_id,
        remitente_id=remitente_id,
        contenido=contenido,
        tipo=tipo,
        reply_a_id=reply_a_id,
        metadatos=metadatos,
    )
    
    return {"data": mensaje.model_dump()}


@router.get("/{mensaje_id}")
async def obtener_mensaje(
    mensaje_id: int = Path(...),
    usuario_id: int = Query(...),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
):
    """Obtener detalle de mensaje.
    
    Solo participantes de la conversación pueden ver.
    """
    caso = ObtenerMensajeUseCase(mensaje_repo, participante_repo)
    mensaje = await caso.ejecutar(mensaje_id, usuario_id)
    
    return {"data": mensaje.model_dump()}


@router.get("")
async def listar_mensajes(
    conversacion_id: int = Query(...),
    usuario_id: int = Query(...),
    limite: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
):
    """Listar mensajes de una conversación.
    
    Ordenados por enviado_en ASC.
    """
    caso = ListarMensajesUseCase(conversacion_repo, participante_repo, mensaje_repo)
    mensajes = await caso.ejecutar(
        conversacion_id=conversacion_id,
        usuario_id=usuario_id,
        limite=limite,
        offset=offset,
    )
    
    return {
        "data": [m.model_dump() for m in mensajes],
        "pagination": {
            "limite": limite,
            "offset": offset,
            "total": len(mensajes),
        }
    }


@router.post("/{mensaje_id}/leer", status_code=status.HTTP_204_NO_CONTENT)
async def marcar_mensaje_leido(
    mensaje_id: int = Path(...),
    usuario_id: int = Body(...),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
    lectura_repo: MensajesLecturasRepository = Depends(get_lectura_repo),
    # websocket_service: WebSocketService = Depends(get_websocket_service),
):
    """Marcar mensaje como leído (US-COM-003).
    
    Idempotente (no falla si ya está leído).
    """
    # TODO: Inyectar websocket_service cuando esté implementado
    websocket_service = WebSocketServiceMock()
    
    caso = MarcarMensajeLeidoUseCase(
        mensaje_repo,
        participante_repo,
        lectura_repo,
        websocket_service,
    )
    
    await caso.ejecutar(mensaje_id, usuario_id)
    return


@router.get("/conversacion/{conversacion_id}/no-leidos")
async def contar_no_leidos(
    conversacion_id: int = Path(...),
    usuario_id: int = Query(...),
    conversacion_repo: ConversacionesRepository = Depends(get_conversacion_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
):
    """Contar mensajes no leídos en conversación (US-COM-003)."""
    caso = ContarNoLeidosUseCase(conversacion_repo, participante_repo, mensaje_repo)
    count = await caso.ejecutar(conversacion_id, usuario_id)
    
    return {"data": {"no_leidos": count}}


@router.get("/buscar")
async def buscar_mensajes(
    usuario_id: int = Query(...),
    termino: str = Query(..., min_length=1),
    limite: int = Query(20, ge=1, le=100),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
):
    """Buscar mensajes por contenido."""
    caso = BuscarMensajesUseCase(mensaje_repo)
    mensajes = await caso.ejecutar(usuario_id, termino, limite)
    
    return {"data": [m.model_dump() for m in mensajes]}


@router.post("/{mensaje_id}/adjuntos", status_code=status.HTTP_201_CREATED)
async def subir_adjunto(
    mensaje_id: int = Path(...),
    usuario_id: int = Query(...),
    tipo: TipoAdjunto = Query(...),
    archivo: UploadFile = File(...),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
    adjunto_repo: MensajesAdjuntosRepository = Depends(get_adjunto_repo),
    # storage_service: StorageService = Depends(get_storage_service),
):
    """Subir archivo adjunto a mensaje.
    
    Validaciones:
    - Tipo MIME permitido
    - Tamaño según tipo de adjunto
    """
    # TODO: Inyectar storage_service cuando esté implementado
    
    storage_service = StorageServiceMock()
    
    # Leer archivo
    archivo_bytes = await archivo.read()
    
    caso = SubirAdjuntoUseCase(
        mensaje_repo,
        participante_repo,
        adjunto_repo,
        storage_service,
    )
    
    adjunto = await caso.ejecutar(
        mensaje_id=mensaje_id,
        usuario_id=usuario_id,
        archivo_bytes=archivo_bytes,
        nombre_archivo=archivo.filename or "archivo",
        mime_type=archivo.content_type or "application/octet-stream",
        tipo=tipo,
    )
    
    return {"data": adjunto.model_dump()}


@router.get("/{mensaje_id}/adjuntos")
async def listar_adjuntos(
    mensaje_id: int = Path(...),
    usuario_id: int = Query(...),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
    adjunto_repo: MensajesAdjuntosRepository = Depends(get_adjunto_repo),
):
    """Listar adjuntos de un mensaje."""
    caso = ListarAdjuntosUseCase(mensaje_repo, participante_repo, adjunto_repo)
    adjuntos = await caso.ejecutar(mensaje_id, usuario_id)
    
    return {"data": [a.model_dump() for a in adjuntos]}


@router.delete("/adjuntos/{adjunto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_adjunto(
    adjunto_id: int = Path(...),
    usuario_id: int = Query(...),
    mensaje_repo: MensajesRepository = Depends(get_mensaje_repo),
    participante_repo: ConversacionesParticipantesRepository = Depends(get_participante_repo),
    adjunto_repo: MensajesAdjuntosRepository = Depends(get_adjunto_repo),
    # storage_service: StorageService = Depends(get_storage_service),
):
    """Eliminar adjunto de mensaje."""
    # TODO: Inyectar storage_service cuando esté implementado

    storage_service = StorageServiceMock()
    
    caso = EliminarAdjuntoUseCase(
        mensaje_repo,
        participante_repo,
        adjunto_repo,
        storage_service,
    )
    
    await caso.ejecutar(adjunto_id, usuario_id)
    return
