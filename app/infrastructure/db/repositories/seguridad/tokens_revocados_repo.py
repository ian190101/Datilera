# app/infrastructure/db/repositories/seguridad/tokens_revocados_repo.py
from __future__ import annotations
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import TokenRevocado

class TokensRevocadosRepository(BaseRepository[TokenRevocado]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TokenRevocado)

    async def esta_revocado(self, jti: str) -> bool:
        res = await self.session.execute(select(TokenRevocado).where(TokenRevocado.jti == jti).limit(1))
        return res.scalar_one_or_none() is not None

    async def revocar(self, jti: str, tipo: str = "refresh") -> None:
        await self.session.execute(insert(TokenRevocado).values(jti=jti, tipo=tipo))
