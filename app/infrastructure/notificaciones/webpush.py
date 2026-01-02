# app/infrastructure/notificaciones/webpush.py

from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.kernel.domain.comunicaciones.ports import WebPushServicePort
from app.infrastructure.db.session import get_session  # o tu helper de DI


class WebPushService(WebPushServicePort):
    """Implementación infraestructura de WebPushServicePort."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def registrar_suscripcion(
        self,
        usuario_id: int,
        sede_id: int,
        endpoint: str,
        claves: Dict[str, Any],
        user_agent: str | None = None,
    ) -> None:
        # TODO: guardar en tabla webpush_suscripciones (modelo + repo)
        # - usuarioid, sedeid, endpoint, p256dh, auth, useragent, creadoen, actualizadoen, activo
        ...

    async def eliminar_suscripcion(self, usuario_id: int, endpoint: str) -> None:
        # TODO: marcar suscripción como inactiva o eliminar fila
        ...

    async def enviar_webpush_a_usuarios(
        self,
        usuario_ids: List[int],
        titulo: str,
        cuerpo: str,
        data: Dict[str, Any] | None = None,
    ) -> int:
        enviados = 0
        # TODO:
        # 1) consultar suscripciones activas por usuario_ids
        # 2) iterar y enviar con lib de WebPush
        # 3) manejar errores por endpoint inválido -> desactivar suscripción
        return enviados
