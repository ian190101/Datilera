
from typing import List
from pydantic import BaseModel

from app.infrastructure.db.repositories.inventario.categorias import CategoriaRepository
from .crear_categoria import CategoriaResponse

class GetCategoriasResponse(BaseModel):
    categorias: List[CategoriaResponse]

class GetCategorias:
    def __init__(self, repository: CategoriaRepository):
        self.repository = repository

    async def execute(self) -> GetCategoriasResponse:
        categorias = await self.repository.list()
        return GetCategoriasResponse(categorias=[CategoriaResponse.from_orm(categoria) for categoria in categorias])
