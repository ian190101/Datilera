# app/infrastructure/db/repositories/finanzas/precios_turnos_repo.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import PrecioTurno

class PreciosTurnosRepository(BaseRepository[PrecioTurno]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PrecioTurno)

    async def obtener_precio(self, turno_id: int, categoria_pago_id: int, gestion: int) -> PrecioTurno | None:
        stmt = select(PrecioTurno).where(
            PrecioTurno.turno_id == turno_id,
            PrecioTurno.categoria_pago_id == categoria_pago_id,
            PrecioTurno.gestion == gestion
        ).limit(1)
        res = await self.session.execute(stmt)
        return res.scalars().first()
