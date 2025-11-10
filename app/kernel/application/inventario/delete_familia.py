
from app.infrastructure.db.repositories.inventario.familias import FamiliaRepository
from app.kernel.domain.exceptions import EntityNotFoundException

class DeleteFamilia:
    def __init__(self, repository: FamiliaRepository):
        self.repository = repository

    async def execute(self, familia_id: int) -> None:
        familia = await self.repository.get(familia_id)
        if not familia:
            raise EntityNotFoundException(f"Familia con id '{familia_id}' no encontrada.")

        await self.repository.delete(familia_id)
