from pydantic import BaseModel
from app.infrastructure.db.repositories.inscripcion.formularios_inscripcion import FormularioInscripcionRepository
from app.infrastructure.db.repositories.inscripcion.formularios_respuestas import FormularioRespuestaRepository
from app.kernel.domain.exceptions import EntityNotFoundException
from app.infrastructure.db.models.inscripcion import FormularioRespuesta


class AnswerRequest(BaseModel):
    campo: str
    valor: str


class SaveAnswersRequest(BaseModel):
    respuestas: list[AnswerRequest]


class SaveAnswers:
    def __init__(
        self,
        form_repo: FormularioInscripcionRepository,
        answer_repo: FormularioRespuestaRepository,
    ):
        self.form_repo = form_repo
        self.answer_repo = answer_repo

    async def execute(self, form_id: int, request: SaveAnswersRequest) -> None:
        if not await self.form_repo.get_by_id(form_id):
            raise EntityNotFoundException(f"Formulario con id {form_id} no encontrado.")

        # This is a simple implementation that overwrites answers.
        # A more complex one could update existing ones.
        await self.answer_repo.delete(where=[FormularioRespuesta.formulario_id == form_id])

        for answer in request.respuestas:
            new_answer = FormularioRespuesta(
                formulario_id=form_id,
                campo=answer.campo,
                valor=answer.valor,
            )
            await self.answer_repo.create(new_answer)