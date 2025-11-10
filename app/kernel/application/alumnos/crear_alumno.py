
from pydantic import BaseModel, Field
from datetime import date

from app.infrastructure.db.repositories.alumnos.alumnos import AlumnoRepository
from app.infrastructure.db.models.alumnos import Alumno
from app.kernel.domain.exceptions import DuplicatedEntityException

class CreateAlumnoRequest(BaseModel):
    sede_id: int
    tutor_id: int
    nombres: str = Field(..., max_length=120)
    apellidos: str = Field(..., max_length=120)
    fecha_nacimiento: date
    documento: str | None = Field(None, max_length=30)
    direccion: str | None = None
    telefono: str | None = Field(None, max_length=20)

class AlumnoResponse(BaseModel):
    id: int
    codigo: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date

    class Config:
        from_attributes = True

class CreateAlumno:
    def __init__(self, repository: AlumnoRepository):
        self.repository = repository

    async def execute(self, request: CreateAlumnoRequest) -> AlumnoResponse:
        # Generate unique code
        # For now, a simple random string. This should be more robust.
        import random
        import string
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Check for duplicates
        if await self.repository.one(where=Alumno.codigo == codigo):
            # Regenerate if collision (rare, but possible)
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        new_alumno = Alumno(
            sede_id=request.sede_id,
            tutor_id=request.tutor_id,
            nombres=request.nombres,
            apellidos=request.apellidos,
            fecha_nacimiento=request.fecha_nacimiento,
            documento=request.documento,
            direccion=request.direccion,
            telefono=request.telefono,
            codigo=codigo
        )

        created_alumno = await self.repository.create(new_alumno)

        return AlumnoResponse.from_orm(created_alumno)
