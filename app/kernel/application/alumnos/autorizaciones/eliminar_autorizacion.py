from app.kernel.domain.alumnos.ports import AutorizacionesRetiroRepositoryPort
from app.kernel.domain.alumnos.errors import AutorizacionRetiroNoEncontradaError


class EliminarAutorizacionCU:
    """Eliminar autorización de retiro."""

    def __init__(self, autorizaciones_repo: AutorizacionesRetiroRepositoryPort):
        self.autorizaciones_repo = autorizaciones_repo

    async def ejecutar(self, autorizacion_id: int) -> bool:
        actual = await self.autorizaciones_repo.obtener_por_id(autorizacion_id)
        if not actual:
            raise AutorizacionRetiroNoEncontradaError(autorizacion_id=autorizacion_id)
        return await self.autorizaciones_repo.eliminar(autorizacion_id)
