from app.kernel.domain.alumnos.consentimiento_entidad import ConsentimientoEntidad
from app.kernel.domain.alumnos.ports import ConsentimientosRepositoryPort
from app.kernel.domain.alumnos.errors import ConsentimientoNoEncontradoError


class ObtenerConsentimientosCU:
    """Obtener consentimientos de un alumno."""

    def __init__(self, consentimientos_repo: ConsentimientosRepositoryPort):
        self.consentimientos_repo = consentimientos_repo

    async def ejecutar(self, alumno_id: int) -> ConsentimientoEntidad:
        consentimiento = await self.consentimientos_repo.obtener_por_alumno(alumno_id)
        if not consentimiento:
            raise ConsentimientoNoEncontradoError(alumno_id=alumno_id)
        return consentimiento
