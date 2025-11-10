
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inscripcion import Contrato


class ContratoRepository(BaseRepository[Contrato]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Contrato)
