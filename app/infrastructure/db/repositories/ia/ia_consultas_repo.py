# app/infrastructure/db/repositories/ia/ia_consultas_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.ia import IAConsulta

class IAConsultasRepository(BaseRepository[IAConsulta]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, IAConsulta)
