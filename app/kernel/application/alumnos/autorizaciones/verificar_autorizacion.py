from app.kernel.domain.alumnos.autorizacion_retiro_entidad import AutorizacionRetiroEntidad
from app.kernel.domain.alumnos.ports import AutorizacionesRetiroRepositoryPort
from app.kernel.domain.alumnos.errors import AutorizacionRetiroNoEncontradaError, AutorizacionRetiroInactivaError


class VerificarAutorizacionCU:
    """Verificar si una persona con CI puede retirar a un alumno."""

    def __init__(self, autorizaciones_repo: AutorizacionesRetiroRepositoryPort):
        self.autorizaciones_repo = autorizaciones_repo

    async def ejecutar(self, alumno_id: int, ci_numero: str) -> AutorizacionRetiroEntidad:
        autorizacion = await self.autorizaciones_repo.obtener_por_ci(alumno_id, ci_numero.strip())
        if not autorizacion:
            raise AutorizacionRetiroNoEncontradaError(ci=ci_numero)
        if not autorizacion.activo:
            raise AutorizacionRetiroInactivaError(autorizacion_id=autorizacion.id)
        return autorizacion
