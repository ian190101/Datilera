# app/application/inscripcion/formularios/rechazar_formulario.py
from pydantic import BaseModel
from app.kernel.domain.inscripcion import EstadoFormulario
from app.kernel.domain.inscripcion.ports import FormularioInscripcionRepositoryPort
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado, FormularioEstadoInvalido

class RechazarFormularioCommand(BaseModel):
    formulario_id: int
    observaciones: str | None = None

class RechazarFormularioUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort):
        self.form_repo = form_repo

    async def execute(self, cmd: RechazarFormularioCommand) -> None:
        form = await self.form_repo.obtener_por_id(cmd.formulario_id)
        if not form:
            raise FormularioNoEncontrado(cmd.formulario_id)
        if form.estado.value != EstadoFormulario.ENVIADO.value:
            raise FormularioEstadoInvalido(form.estado.value, "rechazar")
        form.observaciones = (cmd.observaciones or "").strip() or None
        await self.form_repo.guardar(form)
        await self.form_repo.cambiar_estado(cmd.formulario_id, EstadoFormulario.RECHAZADO)
