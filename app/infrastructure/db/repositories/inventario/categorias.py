
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inventario import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Categoria)
