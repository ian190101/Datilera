
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inscripcion import FormularioRespuesta


class FormularioRespuestaRepository(BaseRepository[FormularioRespuesta]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, FormularioRespuesta)
