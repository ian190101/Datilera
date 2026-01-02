from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.acceso.codigos_acceso import CodigoAccesoUso

class CodigosAccesoUsosRepository(BaseRepository[CodigoAccesoUso]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CodigoAccesoUso)

    async def registrar(self, uso: CodigoAccesoUso) -> None:
        self.session.add(uso)

    async def contar_consumos_exitosos(self, codigo_id: int) -> int:
        stmt = select(func.count(CodigoAccesoUso.id)).where(CodigoAccesoUso.codigo_id == codigo_id)
        return await self.session.scalar(stmt) or 0