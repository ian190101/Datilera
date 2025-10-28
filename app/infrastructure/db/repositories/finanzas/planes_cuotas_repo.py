# app/infrastructure/db/repositories/finanzas/planes_cuotas_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import PlanCuota

class PlanesCuotasRepository(BaseRepository[PlanCuota]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PlanCuota)
