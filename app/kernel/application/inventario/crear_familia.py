
from pydantic import BaseModel, Field

from app.infrastructure.db.repositories.inventario.familias import FamiliaRepository
from app.infrastructure.db.models.inventario import Familia
from app.kernel.domain.exceptions import DuplicatedEntityException

class CreateFamiliaRequest(BaseModel):
    nombre: str = Field(..., max_length=80)
    descripcion: str | None = Field(None, max_length=200)

class FamiliaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    activo: bool

    class Config:
        from_attributes = True

class CreateFamilia:
    def __init__(self, repository: FamiliaRepository):
        self.repository = repository

    async def execute(self, request: CreateFamiliaRequest) -> FamiliaResponse:
        if await self.repository.one(where=Familia.nombre == request.nombre):
            raise DuplicatedEntityException(f"La familia '{request.nombre}' ya existe.")

        new_familia = Familia(
            nombre=request.nombre,
            descripcion=request.descripcion
        )

        created_familia = await self.repository.create(new_familia)

        return FamiliaResponse.from_orm(created_familia)
