# app/infrastructure/db/repositories/finanzas/planes_pago_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import PlanPago

class PlanesPagoRepository(BaseRepository[PlanPago]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PlanPago)
