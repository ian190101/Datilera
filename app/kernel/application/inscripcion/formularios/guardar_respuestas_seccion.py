# app/application/inscripcion/formularios/guardar_respuestas_seccion.py
from typing import Dict
from pydantic import BaseModel, Field
from app.kernel.domain.inscripcion.ports import FormularioRespuestaRepositoryPort, FormularioInscripcionRepositoryPort
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado, SedeNoCoincide

class GuardarRespuestasSeccionCommand(BaseModel):
    formulario_id: int
    sede_id: int
    seccion: str = Field(min_length=1, max_length=40)
    datos: Dict[str, object]

class GuardarRespuestasSeccionUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort, resp_repo: FormularioRespuestaRepositoryPort):
        self.form_repo = form_repo
        self.resp_repo = resp_repo

    async def execute(self, cmd: GuardarRespuestasSeccionCommand) -> None:
        form = await self.form_repo.obtener_por_id(cmd.formulario_id)
        if not form:
            raise FormularioNoEncontrado(cmd.formulario_id)
        if form.sede_id != cmd.sede_id:
            raise SedeNoCoincide("formulario", cmd.sede_id, form.sede_id)
        await self.resp_repo.upsert_seccion(cmd.formulario_id, cmd.seccion, cmd.datos)
