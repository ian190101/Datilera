from pydantic import BaseModel
from datetime import datetime
from app.infrastructure.db.repositories.inscripcion.formularios_inscripcion import FormularioInscripcionRepository
from app.infrastructure.db.repositories.inscripcion.formularios_respuestas import FormularioRespuestaRepository
from app.kernel.domain.exceptions import EntityNotFoundException


class FormularioRespuestaResponse(BaseModel):
    campo: str
    valor: str

    class Config:
        from_attributes = True


class FormularioDetailResponse(BaseModel):
    id: int
    alumno_id: int
    sede_id: int
    gestion: int
    estado: str
    observaciones: str | None
    creado_en: datetime
    actualizado_en: datetime
    respuestas: list[FormularioRespuestaResponse]

    class Config:
        from_attributes = True


class GetFormulario:
    def __init__(
        self,
        form_repo: FormularioInscripcionRepository,
        answer_repo: FormularioRespuestaRepository,
    ):
        self.form_repo = form_repo
        self.answer_repo = answer_repo

    async def execute(self, form_id: int) -> FormularioDetailResponse:
        formulario = await self.form_repo.get_by_id(form_id)
        if not formulario:
            raise EntityNotFoundException(f"Formulario con id {form_id} no encontrado.")

        respuestas = await self.answer_repo.find(where={"formulario_id": form_id})

        # Convertir el objeto formulario a un diccionario y añadir las respuestas
        formulario_dict = formulario.__dict__
        formulario_dict["respuestas"] = [
            FormularioRespuestaResponse.from_orm(res).__dict__ for res in respuestas
        ]

        return FormularioDetailResponse.parse_obj(formulario_dict)
