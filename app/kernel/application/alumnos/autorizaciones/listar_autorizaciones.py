from typing import List

from app.kernel.domain.alumnos.autorizacion_retiro_entidad import AutorizacionRetiroEntidad
from app.kernel.domain.alumnos.ports import AutorizacionesRetiroRepositoryPort


class ListarAutorizacionesCU:
    """Listar autorizaciones de retiro de un alumno."""

    def __init__(self, autorizaciones_repo: AutorizacionesRetiroRepositoryPort):
        self.autorizaciones_repo = autorizaciones_repo

    async def ejecutar(self, alumno_id: int, solo_activas: bool = True) -> List[AutorizacionRetiroEntidad]:
        return await self.autorizaciones_repo.listar_por_alumno(alumno_id, solo_activas=solo_activas)
