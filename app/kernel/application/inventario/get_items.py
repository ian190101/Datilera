from typing import List
from pydantic import BaseModel, ConfigDict
from app.infrastructure.db.repositories.inventario.items_repo import ItemsRepository

class ItemResponse(BaseModel):
    id: int
    categoria_id: int
    codigo: str
    nombre: str
    descripcion: str | None
    precio_unitario: float | int
    unidad_medida: str
    activo: bool
    model_config = ConfigDict(from_attributes=True)

class GetItemsResponse(BaseModel):
    items: List[ItemResponse]

class GetItems:
    def __init__(self, repository: ItemsRepository):
        self.repository = repository

    async def execute(self) -> GetItemsResponse:
        items = await self.repository.list()
        return GetItemsResponse(
            items=[ItemResponse.model_validate(it, from_attributes=True) for it in items]
        )
