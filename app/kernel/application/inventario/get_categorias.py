from typing import List
from pydantic import BaseModel, ConfigDict
from app.infrastructure.db.repositories.inventario.categorias_repo import CategoriasRepository

class CategoriaResponse(BaseModel):
    id: int
    familia_id: int
    nombre: str
    descripcion: str | None
    activo: bool
    model_config = ConfigDict(from_attributes=True)

class GetCategoriasResponse(BaseModel):
    categorias: List[CategoriaResponse]

class GetCategorias:
    def __init__(self, repository: CategoriasRepository):
        self.repository = repository

    async def execute(self) -> GetCategoriasResponse:
        categorias = await self.repository.list()
        return GetCategoriasResponse(
            categorias=[CategoriaResponse.model_validate(c, from_attributes=True) for c in categorias]
        )
