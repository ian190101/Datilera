# app/infrastructure/tasks/notificaciones.py

from celery import shared_task
from app.infrastructure.db.session import get_session
from app.infrastructure.db.repositories.comunicaciones.notificaciones_repo import NotificacionesRepository
from app.kernel.domain.comunicaciones import CanalNotificacion

@shared_task(name="enviar_notificacion_masiva")
def enviar_notificacion_masiva_task(
    destinatarios: list[int],
    titulo: str,
    cuerpo: str,
    tipo: str,
    canal: str = "in_app",
    prioridad: str = "media",
    programada_para: str | None = None,
    metadatos: dict | None = None,
):
    """Tarea asíncrona para envío masivo de notificaciones."""
    import asyncio
    from datetime import datetime
    
    async def _ejecutar():
        async with get_session() as session:
            repo = NotificacionesRepository(session)
            
            for usuario_id in destinatarios:
                await repo.crear(
                    usuario_id=usuario_id,
                    titulo=titulo,
                    cuerpo=cuerpo,
                    tipo=tipo,
                    canal=CanalNotificacion(canal),
                    prioridad=prioridad,
                    programada_para=datetime.fromisoformat(programada_para) if programada_para else None,
                    metadatos=metadatos,
                )
            
            await session.commit()
    
    asyncio.run(_ejecutar())
    return {"procesados": len(destinatarios)}
