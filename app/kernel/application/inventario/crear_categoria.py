
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.inventario.categorias import CategoriaRepository
from app.infrastructure.db.models.inventario import Categoria
from app.kernel.domain.exceptions import DuplicatedEntityException

class CreateCategoriaRequest(BaseModel):
    familia_id: int
    nombre: str = Field(..., max_length=80)
    descripcion: str | None = Field(None, max_length=200)

class CategoriaResponse(BaseModel):
    id: int
    familia_id: int
    nombre: str
    descripcion: str | None
    activo: bool

    class Config:
        from_attributes = True

class CreateCategoria:
    def __init__(self, repository: CategoriaRepository):
        self.repository = repository

    async def execute(self, request: CreateCategoriaRequest) -> CategoriaResponse:
        if await self.repository.one(where=(Categoria.nombre == request.nombre, Categoria.familia_id == request.familia_id)):
            raise DuplicatedEntityException(f"La categoría '{request.nombre}' ya existe en esta familia.")

        new_categoria = Categoria(
            familia_id=request.familia_id,
            nombre=request.nombre,
            descripcion=request.descripcion
        )

        created_categoria = await self.repository.create(new_categoria)

        return CategoriaResponse.from_orm(created_categoria)
