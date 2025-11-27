# app/infrastructure/db/repositories/inscripcion/formularios_inscripcion_repo.py
from sqlalchemy import update  # <-- esto es nuevo
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inscripcion import FormularioInscripcion


class FormularioInscripcionRepository(BaseRepository[FormularioInscripcion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, FormularioInscripcion)
    async def fijar_turno(self, formulario_id: int, turno_id: int) -> None:  # <-- esto es nuevo
        await self.session.execute(  # <-- esto es nuevo
            update(FormularioInscripcion).where(FormularioInscripcion.id == formulario_id).values(turno_id=turno_id)  # <-- esto es nuevo
        )  # <-- esto es nuevo
