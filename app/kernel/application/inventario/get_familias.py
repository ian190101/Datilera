
from typing import List
from pydantic import BaseModel

from app.infrastructure.db.repositories.inventario.familias import FamiliaRepository
from .crear_familia import FamiliaResponse

class GetFamiliasResponse(BaseModel):
    familias: List[FamiliaResponse]

class GetFamilias:
    def __init__(self, repository: FamiliaRepository):
        self.repository = repository

    async def execute(self) -> GetFamiliasResponse:
        familias = await self.repository.list()
        return GetFamiliasResponse(familias=[FamiliaResponse.from_orm(familia) for familia in familias])
