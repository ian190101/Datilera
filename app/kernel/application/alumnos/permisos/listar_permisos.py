from typing import List, Optional

from app.kernel.domain.alumnos.permiso_personal_entidad import PermisoPersonalEntidad
from app.kernel.domain.alumnos.ports import PermisosPersonalRepositoryPort


class ListarPermisosCU:
    """Listar permisos por sede o por persona."""

    def __init__(self, permisos_repo: PermisosPersonalRepositoryPort):
        self.permisos_repo = permisos_repo

    async def por_sede(self, sede_id: int, estado: Optional[str] = None) -> List[PermisoPersonalEntidad]:
        return await self.permisos_repo.listar_por_sede(sede_id, estado)

    async def por_personal(self, personal_id: int) -> List[PermisoPersonalEntidad]:
        return await self.permisos_repo.listar_por_personal(personal_id)
