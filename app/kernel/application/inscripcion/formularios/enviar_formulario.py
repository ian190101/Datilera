# app/application/inscripcion/formularios/enviar_formulario.py
from pydantic import BaseModel
from app.kernel.domain.inscripcion import EstadoFormulario
from app.kernel.domain.inscripcion.ports import FormularioInscripcionRepositoryPort
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado, FormularioEstadoInvalido

class EnviarFormularioCommand(BaseModel):
    formulario_id: int

class EnviarFormularioUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort):
        self.form_repo = form_repo

    async def execute(self, cmd: EnviarFormularioCommand) -> None:
        form = await self.form_repo.obtener_por_id(cmd.formulario_id)
        if not form:
            raise FormularioNoEncontrado(cmd.formulario_id)
        if form.estado.value != EstadoFormulario.BORRADOR.value:
            raise FormularioEstadoInvalido(form.estado.value, "enviar")
        await self.form_repo.cambiar_estado(cmd.formulario_id, EstadoFormulario.ENVIADO)
