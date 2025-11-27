# app/application/inscripcion/formularios/preseleccionar_turno.py
from pydantic import BaseModel
from app.kernel.domain.inscripcion import EstadoFormulario
from app.kernel.domain.inscripcion.ports import FormularioInscripcionRepositoryPort
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado, FormularioEstadoInvalido

class PreseleccionarTurnoCommand(BaseModel):
    formulario_id: int
    turno_id: int

class PreseleccionarTurnoUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort):
        self.form_repo = form_repo

    async def execute(self, cmd: PreseleccionarTurnoCommand) -> None:
        form = await self.form_repo.obtener_por_id(cmd.formulario_id)
        if not form:
            raise FormularioNoEncontrado(cmd.formulario_id)
        if form.estado.value != EstadoFormulario.ENVIADO.value:
            raise FormularioEstadoInvalido(form.estado.value, "preseleccionar turno")
        await self.form_repo.fijar_turno(cmd.formulario_id, cmd.turno_id)
