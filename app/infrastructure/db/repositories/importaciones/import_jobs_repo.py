# app/infrastructure/db/repositories/importaciones/import_jobs_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.importaciones import ImportJob

class ImportJobsRepository(BaseRepository[ImportJob]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ImportJob)
