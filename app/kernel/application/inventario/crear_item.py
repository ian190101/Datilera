from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from app.infrastructure.db.repositories.inventario.items_repo import ItemsRepository
from app.infrastructure.db.models.inventario import Item
from app.kernel.domain.common.excepciones import AlreadyExistsError

class CreateItemRequest(BaseModel):
    categoria_id: int
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=120)
    descripcion: str | None = None
    precio_unitario: Decimal
    unidad_medida: str = Field("unidad", max_length=20)

class ItemResponse(BaseModel):
    id: int
    categoria_id: int
    codigo: str
    nombre: str
    descripcion: str | None
    precio_unitario: Decimal
    unidad_medida: str
    activo: bool
    model_config = ConfigDict(from_attributes=True)

class CreateItem:
    def __init__(self, repository: ItemsRepository):
        self.repository = repository

    async def execute(self, request: CreateItemRequest) -> ItemResponse:
        if await self.repository.one(where=Item.codigo == request.codigo):
            raise AlreadyExistsError(f"El código '{request.codigo}' ya existe.")
        new_item = Item(
            categoria_id=request.categoria_id,
            codigo=request.codigo,
            nombre=request.nombre,
            descripcion=request.descripcion,
            precio_unitario=request.precio_unitario,
            unidad_medida=request.unidad_medida,
        )
        created = await self.repository.create(new_item)
        return ItemResponse.model_validate(created, from_attributes=True)
