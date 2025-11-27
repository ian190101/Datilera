from app.kernel.domain.alumnos.ports import AutorizacionesRetiroRepositoryPort
from app.kernel.domain.alumnos.errors import AutorizacionRetiroNoEncontradaError


class DesactivarAutorizacionCU:
    """Desactivar una autorización de retiro."""

    def __init__(self, autorizaciones_repo: AutorizacionesRetiroRepositoryPort):
        self.autorizaciones_repo = autorizaciones_repo

    async def ejecutar(self, autorizacion_id: int):
        actual = await self.autorizaciones_repo.obtener_por_id(autorizacion_id)
        if not actual:
            raise AutorizacionRetiroNoEncontradaError(autorizacion_id=autorizacion_id)
        return await self.autorizaciones_repo.desactivar(autorizacion_id)
