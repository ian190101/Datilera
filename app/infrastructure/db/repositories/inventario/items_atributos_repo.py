# app/infrastructure/db/repositories/inventario/items_atributos_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.inventario import ItemAtributo

class ItemsAtributosRepository(BaseRepository[ItemAtributo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ItemAtributo)
