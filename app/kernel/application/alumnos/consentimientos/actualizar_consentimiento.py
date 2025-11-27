from datetime import datetime

from app.kernel.domain.alumnos.consentimiento_entidad import ConsentimientoEntidad
from app.kernel.domain.alumnos.ports import ConsentimientosRepositoryPort
from app.kernel.domain.alumnos.errors import ConsentimientoNoEncontradoError


class ActualizarConsentimientosCU:
    """Actualizar consentimientos de un alumno."""

    def __init__(self, consentimientos_repo: ConsentimientosRepositoryPort):
        self.consentimientos_repo = consentimientos_repo

    async def ejecutar(
        self,
        alumno_id: int,
        uso_imagen: bool,
        actividades_externas: bool,
        atencion_medica_emergencia: bool,
        transporte_autorizado: bool,
        publicacion_trabajos: bool,
        actualizado_por_id: int,
    ) -> ConsentimientoEntidad:
        consentimiento = await self.consentimientos_repo.obtener_por_alumno(alumno_id)
        if not consentimiento:
            raise ConsentimientoNoEncontradoError(alumno_id=alumno_id)

        consentimiento.uso_imagen = uso_imagen
        consentimiento.actividades_externas = actividades_externas
        consentimiento.atencion_medica_emergencia = atencion_medica_emergencia
        consentimiento.transporte_autorizado = transporte_autorizado
        consentimiento.publicacion_trabajos = publicacion_trabajos
        consentimiento.actualizado_en = datetime.utcnow()
        consentimiento.actualizado_por_id = actualizado_por_id

        return await self.consentimientos_repo.actualizar(alumno_id, consentimiento)
