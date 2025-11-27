# app/application/inscripcion/formularios/reabrir_formulario.py
from typing import Literal, Optional
from pydantic import BaseModel, Field
from app.kernel.domain.inscripcion import EstadoFormulario
from app.kernel.domain.inscripcion.ports import FormularioInscripcionRepositoryPort
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado, FormularioEstadoInvalido

DestinoEstado = Literal["enviado", "borrador"]

class ReabrirFormularioCommand(BaseModel):
    formulario_id: int
    destino: DestinoEstado = Field(pattern="^(enviado|borrador)$")
    observaciones: Optional[str] = None

class ReabrirFormularioUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort):
        self.form_repo = form_repo

    async def execute(self, cmd: ReabrirFormularioCommand) -> None:
        form = await self.form_repo.obtener_por_id(cmd.formulario_id)
        if not form:
            raise FormularioNoEncontrado(cmd.formulario_id)
        if form.estado.value not in (EstadoFormulario.APROBADO.value, EstadoFormulario.RECHAZADO.value):
            raise FormularioEstadoInvalido(form.estado.value, "reabrir")
        form.observaciones = (cmd.observaciones or "").strip() or None
        await self.form_repo.guardar(form)
        nuevo = EstadoFormulario.ENVIADO if cmd.destino == "enviado" else EstadoFormulario.BORRADOR
        await self.form_repo.cambiar_estado(cmd.formulario_id, nuevo)
