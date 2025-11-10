
from pydantic import BaseModel
from typing import List

from app.infrastructure.db.repositories.inscripcion.formularios_inscripcion import FormularioInscripcionRepository
from app.infrastructure.db.repositories.inscripcion.formularios_respuestas import FormularioRespuestaRepository
from app.infrastructure.db.models.inscripcion import FormularioInscripcion, FormularioRespuesta, EstadoFormulario
from app.kernel.domain.exceptions import EntityNotFoundException

class AnswerResponse(BaseModel):
    campo: str
    valor: str

class FormularioDetailResponse(BaseModel):
    id: int
    alumno_id: int
    sede_id: int
    gestion: int
    estado: EstadoFormulario
    answers: List[AnswerResponse]

    class Config:
        from_attributes = True

class GetFormulario:
    def __init__(self, form_repo: FormularioInscripcionRepository, answer_repo: FormularioRespuestaRepository):
        self.form_repo = form_repo
        self.answer_repo = answer_repo

    async def execute(self, form_id: int) -> FormularioDetailResponse:
        form = await self.form_repo.get(form_id)
        if not form:
            raise EntityNotFoundException(f"Formulario con id '{form_id}' no encontrado.")

        answers = await self.answer_repo.list(where=FormularioRespuesta.formulario_id == form_id)

        return FormularioDetailResponse(
            id=form.id,
            alumno_id=form.alumno_id,
            sede_id=form.sede_id,
            gestion=form.gestion,
            estado=form.estado,
            answers=[AnswerResponse(campo=a.campo, valor=a.valor) for a in answers]
        )
