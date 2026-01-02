# app/interfaces/api/v1/wp.py  (o donde lo tengas)

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Request, status, HTTPException

from pydantic import BaseModel

from app.kernel.domain.comunicaciones.ports import WebPushServicePort
from app.infrastructure.notificaciones.webpush import WebPushService
from app.infrastructure.auth.jwt import decode_token  # mismo decode que ws.py [file:34]

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


class WebPushSuscripcionIn(BaseModel):
    endpoint: str
    keys: dict


def get_webpush_service() -> WebPushServicePort:
    # TODO: inyectar AsyncSession vía Depends y crear WebPushService
    ...


def _get_user_sede_from_request(request: Request) -> tuple[int, int]:
    """
    Extrae el JWT del header Authorization y devuelve (user_id, sede_id),
    igual que ws.py usa sub y sede_id del payload. [file:34]
    """
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no provisto",
        )

    token = auth.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    user_id = int(payload["sub"])
    sede_id = int(payload["sede_id"])
    return user_id, sede_id


@router.post(
    "/webpush/suscripcion",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def registrar_webpush_suscripcion(
    payload: WebPushSuscripcionIn,
    request: Request,
    webpush_service: WebPushServicePort = Depends(get_webpush_service),
):
    user_id, sede_id = _get_user_sede_from_request(request)
    ua = request.headers.get("user-agent")

    await webpush_service.registrar_suscripcion(
        usuario_id=user_id,
        sede_id=sede_id,
        endpoint=payload.endpoint,
        claves=payload.keys,
        user_agent=ua,
    )


@router.delete(
    "/webpush/suscripcion",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def eliminar_webpush_suscripcion(
    payload: WebPushSuscripcionIn,
    request: Request,
    webpush_service: WebPushServicePort = Depends(get_webpush_service),
):
    user_id, _ = _get_user_sede_from_request(request)

    await webpush_service.eliminar_suscripcion(
        usuario_id=user_id,
        endpoint=payload.endpoint,
    )
