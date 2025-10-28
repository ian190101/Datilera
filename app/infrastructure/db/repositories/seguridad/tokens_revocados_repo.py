# app/infrastructure/db/repositories/seguridad/tokens_revocados_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.seguridad import TokenRevocado

class TokensRevocadosRepository(BaseRepository[TokenRevocado]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TokenRevocado)
