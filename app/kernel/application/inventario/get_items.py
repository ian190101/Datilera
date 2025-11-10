
from typing import List
from pydantic import BaseModel

from app.infrastructure.db.repositories.inventario.items import ItemRepository
from .crear_item import ItemResponse

class GetItemsResponse(BaseModel):
    items: List[ItemResponse]

class GetItems:
    def __init__(self, repository: ItemRepository):
        self.repository = repository

    async def execute(self) -> GetItemsResponse:
        items = await self.repository.list()
        return GetItemsResponse(items=[ItemResponse.from_orm(item) for item in items])
