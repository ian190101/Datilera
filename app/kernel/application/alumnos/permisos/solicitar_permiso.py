from datetime import datetime, date

from app.kernel.domain.alumnos.permiso_personal_entidad import PermisoPersonalEntidad
from app.kernel.domain.alumnos.ports import PermisosPersonalRepositoryPort
from app.kernel.domain.alumnos.errors import PermisoFechasInvalidasError


class SolicitarPermisoCU:
    """Crear solicitud de permiso para personal."""

    def __init__(self, permisos_repo: PermisosPersonalRepositoryPort):
        self.permisos_repo = permisos_repo

    async def ejecutar(
        self,
        personal_id: int,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        tipo_permiso: str,
        motivo: str,
    ) -> PermisoPersonalEntidad:
        permiso = PermisoPersonalEntidad(
            personal_id=personal_id,
            sede_id=sede_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tipo_permiso=tipo_permiso,
            motivo=motivo,
            estado="pendiente",
            creado_en=datetime.utcnow(),
        )
        if not permiso.validar_fechas():
            raise PermisoFechasInvalidasError()
        return await self.permisos_repo.crear(permiso)
