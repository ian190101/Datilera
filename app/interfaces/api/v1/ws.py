from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from app.config.settings import Settings
from app.infrastructure.auth.jwt import decode_token  # ya existe en authutils/jwt
from app.infrastructure.ws.manager import ws_manager, ConnectionInfo

router = APIRouter()


async def _get_user_from_token(token: str) -> Optional[ConnectionInfo]:
    """
    Decodifica el JWT y construye ConnectionInfo.
    Ajusta las claves según tu payload real (sub, sede_id, etc.).
    """
    payload = decode_token(token)
    if payload is None:
        return None

    user_id = int(payload["sub"])
    sede_id = int(payload["sede_id"])
    return ConnectionInfo(user_id=user_id, sede_id=sede_id)


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket) -> None:
    # Estrategia simple: token en query param ?token=...
    token: Optional[str] = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    info = await _get_user_from_token(token)
    if info is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(info, websocket)

    try:
        while True:
            # Por ahora solo consumimos mensajes de control del cliente.
            # Más adelante puedes soportar mensajes tipo "ping" o comandos.
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(info, websocket)
    except Exception:
        ws_manager.disconnect(info, websocket)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
