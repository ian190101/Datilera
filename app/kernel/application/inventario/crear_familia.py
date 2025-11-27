from pydantic import BaseModel, Field, ConfigDict
from app.infrastructure.db.repositories.inventario.familias_repo import FamiliasRepository
from app.infrastructure.db.models.inventario import Familia
from app.kernel.domain.common.excepciones import AlreadyExistsError

class CreateFamiliaRequest(BaseModel):
    nombre: str = Field(..., max_length=80)
    descripcion: str | None = Field(None, max_length=200)

class FamiliaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    activo: bool
    model_config = ConfigDict(from_attributes=True)

class CreateFamilia:
    def __init__(self, repository: FamiliasRepository):
        self.repository = repository

    async def execute(self, request: CreateFamiliaRequest) -> FamiliaResponse:
        if await self.repository.one(where=Familia.nombre == request.nombre):
            raise AlreadyExistsError(f"La familia '{request.nombre}' ya existe.")
        new_familia = Familia(nombre=request.nombre, descripcion=request.descripcion)
        created = await self.repository.create(new_familia)
        return FamiliaResponse.model_validate(created, from_attributes=True)
