# app/application/inscripcion/formularios/marcar_aprobado.py
from pydantic import BaseModel
from app.kernel.domain.inscripcion import EstadoFormulario
from app.kernel.domain.inscripcion.ports import FormularioInscripcionRepositoryPort
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado, FormularioEstadoInvalido

class MarcarAprobadoCommand(BaseModel):
    formulario_id: int
    usuario_id: int

class MarcarAprobadoUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort):
        self.form_repo = form_repo

    async def execute(self, cmd: MarcarAprobadoCommand) -> None:
        form = await self.form_repo.obtener_por_id(cmd.formulario_id)
        if not form:
            raise FormularioNoEncontrado(cmd.formulario_id)
        if form.estado.value not in (EstadoFormulario.ENVIADO.value, EstadoFormulario.RECHAZADO.value):
            raise FormularioEstadoInvalido(form.estado.value, "aprobar")
        await self.form_repo.marcar_aprobado(cmd.formulario_id, cmd.usuario_id)
