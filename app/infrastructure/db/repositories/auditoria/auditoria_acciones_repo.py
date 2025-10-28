# app/infrastructure/db/repositories/auditoria/auditoria_acciones_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.auditoria import AuditoriaAccion

class AuditoriaAccionesRepository(BaseRepository[AuditoriaAccion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditoriaAccion)
