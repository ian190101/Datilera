# app/infrastructure/db/repositories/finanzas/pagos_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Pago

class PagosRepository(BaseRepository[Pago]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Pago)

    async def listar_por_alumno(self, alumno_id: int, limit: int = 100, offset: int = 0):
        res = await self.session.execute(
            select(Pago).where(Pago.alumno_id == alumno_id).limit(limit).offset(offset)
        )
        return res.scalars().all()
