# app/application/inscripcion/formularios/validar_prev_aprobar.py
from typing import List, Tuple
from pydantic import BaseModel
from app.kernel.domain.inscripcion import EstadoFormulario
from app.kernel.domain.inscripcion.ports import FormularioInscripcionRepositoryPort, FormularioRespuestaRepositoryPort
from app.kernel.domain.inscripcion.errors import FormularioNoEncontrado, FormularioEstadoInvalido

REQUIRED_CAMPOS: List[Tuple[str, str]] = [
    ("consentimiento_imagen", "general"),
    ("alergias", "salud"),
    ("medicacion", "salud"),
    ("autorizados_recoger", "familia"),
]

class ValidarPrevAprobarCommand(BaseModel):
    formulario_id: int

class ResultadoValidacion(BaseModel):
    ok: bool
    faltantes: List[str]

class ValidarPrevAprobarUseCase:
    def __init__(self, form_repo: FormularioInscripcionRepositoryPort, resp_repo: FormularioRespuestaRepositoryPort):
        self.form_repo = form_repo
        self.resp_repo = resp_repo

    async def execute(self, cmd: ValidarPrevAprobarCommand) -> ResultadoValidacion:
        form = await self.form_repo.obtener_por_id(cmd.formulario_id)
        if not form:
            raise FormularioNoEncontrado(cmd.formulario_id)
        if form.estado.value != EstadoFormulario.ENVIADO.value:
            raise FormularioEstadoInvalido(form.estado.value, "validar para aprobar")
        resps = await self.resp_repo.listar_por_formulario(cmd.formulario_id)
        index = {(r.seccion or "general", r.campo): r.valor for r in resps}
        faltantes: List[str] = []
        for campo, seccion in REQUIRED_CAMPOS:
            if (seccion, campo) not in index or str(index[(seccion, campo)]).strip() == "":
                faltantes.append(f"{seccion}.{campo}")
        return ResultadoValidacion(ok=len(faltantes) == 0, faltantes=faltantes)
