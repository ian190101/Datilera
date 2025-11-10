
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.inventario.familias import FamiliaRepository
from app.kernel.domain.exceptions import EntityNotFoundException

class UpdateFamiliaRequest(BaseModel):
    nombre: str = Field(..., max_length=80)
    descripcion: str | None = Field(None, max_length=200)
    activo: bool

class UpdateFamilia:
    def __init__(self, repository: FamiliaRepository):
        self.repository = repository

    async def execute(self, familia_id: int, request: UpdateFamiliaRequest) -> None:
        familia = await self.repository.get(familia_id)
        if not familia:
            raise EntityNotFoundException(f"Familia con id '{familia_id}' no encontrada.")

        await self.repository.update(familia_id, request.dict())
