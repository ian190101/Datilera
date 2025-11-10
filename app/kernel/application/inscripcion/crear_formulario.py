from pydantic import BaseModel
from app.infrastructure.db.repositories.inscripcion.formularios_inscripcion import FormularioInscripcionRepository
from app.infrastructure.db.repositories.alumnos.alumnos import AlumnoRepository
from app.kernel.domain.exceptions import EntityNotFoundException, DuplicatedEntityException
from app.infrastructure.db.models.inscripcion import FormularioInscripcion


class CreateFormularioRequest(BaseModel):
    alumno_id: int
    sede_id: int
    gestion: int


class FormularioResponse(BaseModel):
    id: int
    alumno_id: int
    estado: str

    class Config:
        from_attributes = True


class CreateFormulario:
    def __init__(
        self,
        form_repo: FormularioInscripcionRepository,
        alumno_repo: AlumnoRepository,
    ):
        self.form_repo = form_repo
        self.alumno_repo = alumno_repo

    async def execute(self, request: CreateFormularioRequest) -> FormularioResponse:
        if not await self.alumno_repo.get_by_id(request.alumno_id):
            raise EntityNotFoundException(f"Alumno con id {request.alumno_id} no encontrado.")

        existing_form = await self.form_repo.one_or_none(
            where=[
                FormularioInscripcion.alumno_id == request.alumno_id,
                FormularioInscripcion.gestion == request.gestion,
            ]
        )
        if existing_form:
            raise DuplicatedEntityException("Ya existe un formulario para este alumno en la gestión actual.")

        new_form = FormularioInscripcion(
            alumno_id=request.alumno_id,
            sede_id=request.sede_id,
            gestion=request.gestion,
            estado="borrador",
        )

        created_form = await self.form_repo.create(new_form)
        return FormularioResponse.from_orm(created_form)