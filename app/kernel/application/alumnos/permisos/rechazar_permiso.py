from datetime import datetime

from app.kernel.domain.alumnos.permiso_personal_entidad import PermisoPersonalEntidad
from app.kernel.domain.alumnos.ports import PermisosPersonalRepositoryPort
from app.kernel.domain.alumnos.errors import (
    PermisoNoEncontradoError,
    PermisoYaAprobadoError,
)


class RechazarPermisoCU:
    """Rechazar una solicitud de permiso."""

    def __init__(self, permisos_repo: PermisosPersonalRepositoryPort):
        self.permisos_repo = permisos_repo

    async def ejecutar(self, permiso_id: int, aprobado_por_id: int) -> PermisoPersonalEntidad:
        permiso = await self.permisos_repo.obtener_por_id(permiso_id)
        if not permiso:
            raise PermisoNoEncontradoError(permiso_id=permiso_id)
        if permiso.estado != "pendiente":
            raise PermisoYaAprobadoError(permiso_id=permiso_id, estado_actual=permiso.estado)

        return await self.permisos_repo.actualizar_estado(
            permiso_id, "rechazado", aprobado_por_id
        )
