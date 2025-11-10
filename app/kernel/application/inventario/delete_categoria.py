
from app.infrastructure.db.repositories.inventario.categorias import CategoriaRepository
from app.kernel.domain.exceptions import EntityNotFoundException

class DeleteCategoria:
    def __init__(self, repository: CategoriaRepository):
        self.repository = repository

    async def execute(self, categoria_id: int) -> None:
        categoria = await self.repository.get(categoria_id)
        if not categoria:
            raise EntityNotFoundException(f"Categoría con id '{categoria_id}' no encontrada.")

        await self.repository.delete(categoria_id)
