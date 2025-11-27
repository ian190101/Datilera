from typing import List
from pydantic import BaseModel, ConfigDict
from app.infrastructure.db.repositories.inventario.familias_repo import FamiliasRepository

class FamiliaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    activo: bool
    model_config = ConfigDict(from_attributes=True)

class GetFamiliasResponse(BaseModel):
    familias: List[FamiliaResponse]

class GetFamilias:
    def __init__(self, repository: FamiliasRepository):
        self.repository = repository

    async def execute(self) -> GetFamiliasResponse:
        familias = await self.repository.list()
        return GetFamiliasResponse(
            familias=[FamiliaResponse.model_validate(f, from_attributes=True) for f in familias]
        )
