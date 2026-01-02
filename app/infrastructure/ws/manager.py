from __future__ import annotations

from collections import defaultdict
from typing import Dict, Set

from fastapi import WebSocket
from pydantic import BaseModel

from app.infrastructure.ws.events import WSBaseEvent, WSEventType


class ConnectionInfo(BaseModel):
    user_id: int
    sede_id: int


class WSConnectionManager:
    def __init__(self) -> None:
        # conexiones por usuario
        self._user_connections: Dict[int, Set[WebSocket]] = defaultdict(set)
        # conexiones por sede
        self._sede_connections: Dict[int, Set[WebSocket]] = defaultdict(set)

    async def connect(self, info: ConnectionInfo, websocket: WebSocket) -> None:
        await websocket.accept()
        self._user_connections[info.user_id].add(websocket)
        self._sede_connections[info.sede_id].add(websocket)

    def disconnect(self, info: ConnectionInfo, websocket: WebSocket) -> None:
        if info.user_id in self._user_connections:
            self._user_connections[info.user_id].discard(websocket)
            if not self._user_connections[info.user_id]:
                del self._user_connections[info.user_id]

        if info.sede_id in self._sede_connections:
            self._sede_connections[info.sede_id].discard(websocket)
            if not self._sede_connections[info.sede_id]:
                del self._sede_connections[info.sede_id]

    async def send_to_user(self, user_id: int, event: WSBaseEvent) -> None:
        connections = self._user_connections.get(user_id, set())
        if not connections:
            return
        message = event.model_dump_json()
        for ws in list(connections):
            await self._safe_send(ws, message)

    async def broadcast_to_sede(self, sede_id: int, event: WSBaseEvent) -> None:
        connections = self._sede_connections.get(sede_id, set())
        if not connections:
            return
        message = event.model_dump_json()
        for ws in list(connections):
            await self._safe_send(ws, message)

    async def send_notif_badge(
        self,
        usuario_id: int,
        sede_id: int,
        total_no_leidas: int,
    ) -> None:
        event = WSBaseEvent(
            type=WSEventType.NOTIF_BADGE,  # enum en events.py
            payload={
                "total_no_leidas": total_no_leidas,
                "sede_id": sede_id,
            },
        )
        await self.send_to_user(usuario_id, event)

    @staticmethod
    async def _safe_send(websocket: WebSocket, message: str) -> None:
        try:
            await websocket.send_text(message)
        except Exception:
            # la desconexión real la maneja el router en el loop
            pass


ws_manager = WSConnectionManager()
