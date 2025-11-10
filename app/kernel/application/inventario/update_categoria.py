
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.inventario.categorias import CategoriaRepository
from app.kernel.domain.exceptions import EntityNotFoundException

class UpdateCategoriaRequest(BaseModel):
    nombre: str = Field(..., max_length=80)
    descripcion: str | None = Field(None, max_length=200)
    activo: bool

class UpdateCategoria:
    def __init__(self, repository: CategoriaRepository):
        self.repository = repository

    async def execute(self, categoria_id: int, request: UpdateCategoriaRequest) -> None:
        categoria = await self.repository.get(categoria_id)
        if not categoria:
            raise EntityNotFoundException(f"Categoría con id '{categoria_id}' no encontrada.")

        await self.repository.update(categoria_id, request.dict())
