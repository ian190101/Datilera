from __future__ import annotations

import time

from fastapi import Request
from loguru import logger

from app.infrastructure.db.repositories.auditoria.auditoria_acciones_repo import AuditoriaAccionesRepository
from app.infrastructure.db.session import AsyncSessionLocal


async def audit_request_middleware(request: Request, call_next):
    if not request.url.path.startswith("/api/v1"):
        return await call_next(request)

    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    principal = getattr(request.state, "auth", None)

    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await AuditoriaAccionesRepository(session).registrar(
                    usuario_id=getattr(principal, "usuario_id", None),
                    sede_id=getattr(principal, "sede_id", None),
                    entidad="api",
                    accion=request.method.lower(),
                    ip=request.client.host if request.client else None,
                    user_agent=(request.headers.get("user-agent") or "")[:1000],
                    metodo_http=request.method,
                    endpoint=request.url.path,
                    codigo_respuesta=response.status_code,
                    duracion_ms=elapsed_ms,
                    exitoso=response.status_code < 400,
                    nivel="error" if response.status_code >= 500 else "warning" if response.status_code >= 400 else "info",
                    contexto={"query_keys": sorted(request.query_params.keys())},
                )
    except Exception as exc:
        # La observabilidad nunca debe derribar la operación principal.
        logger.error(f"No se pudo persistir auditoría HTTP: {exc}")

    return response
