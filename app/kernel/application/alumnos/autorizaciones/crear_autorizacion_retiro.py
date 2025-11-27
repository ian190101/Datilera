from datetime import datetime

from app.kernel.domain.alumnos.autorizacion_retiro_entidad import AutorizacionRetiroEntidad
from app.kernel.domain.alumnos.ports import (
    AlumnoRepositoryPort,
    AutorizacionesRetiroRepositoryPort,
)
from app.kernel.domain.alumnos.errors import (
    AlumnoNoEncontradoError,
    AutorizacionRetiroDuplicadaError,
)


class CrearAutorizacionRetiroCU:
    """Crear autorización de retiro para un alumno."""

    def __init__(
        self,
        alumno_repo: AlumnoRepositoryPort,
        autorizaciones_repo: AutorizacionesRetiroRepositoryPort,
    ):
        self.alumno_repo = alumno_repo
        self.autorizaciones_repo = autorizaciones_repo

    async def ejecutar(
        self,
        alumno_id: int,
        nombres: str,
        apellidos: str,
        ci_numero: str,
        telefono: str,
        relacion: str,
        autorizado_por_id: int,
    ) -> AutorizacionRetiroEntidad:
        alumno = await self.alumno_repo.obtener_por_id(alumno_id)
        if not alumno:
            raise AlumnoNoEncontradoError(alumno_id=alumno_id)

        existente = await self.autorizaciones_repo.obtener_por_ci(alumno_id, ci_numero)
        if existente and existente.activo:
            raise AutorizacionRetiroDuplicadaError(alumno_id=alumno_id, ci=ci_numero)

        autorizacion = AutorizacionRetiroEntidad(
            alumno_id=alumno_id,
            nombres=nombres.strip(),
            apellidos=apellidos.strip(),
            ci_numero=ci_numero.strip(),
            telefono=telefono.strip(),
            relacion=relacion,
            activo=True,
            creado_en=datetime.utcnow(),
            autorizado_por_id=autorizado_por_id,
        )
        return await self.autorizaciones_repo.crear(autorizacion)
