from datetime import datetime

from app.kernel.domain.alumnos.consentimiento_entidad import ConsentimientoEntidad
from app.kernel.domain.alumnos.ports import ConsentimientosRepositoryPort
from app.kernel.domain.alumnos.errors import ConsentimientoNoEncontradoError


class CrearConsentimientosCU:
    """Crear consentimientos iniciales para un alumno (si no existen)."""

    def __init__(self, consentimientos_repo: ConsentimientosRepositoryPort):
        self.consentimientos_repo = consentimientos_repo

    async def ejecutar(
        self,
        alumno_id: int,
        uso_imagen: bool = False,
        actividades_externas: bool = False,
        atencion_medica_emergencia: bool = True,
        transporte_autorizado: bool = False,
        publicacion_trabajos: bool = False,
        actualizado_por_id: int = None,
    ) -> ConsentimientoEntidad:
        existente = await self.consentimientos_repo.obtener_por_alumno(alumno_id)
        if existente:
            # si ya existe, actualizar en vez de crear
            existente.uso_imagen = uso_imagen
            existente.actividades_externas = actividades_externas
            existente.atencion_medica_emergencia = atencion_medica_emergencia
            existente.transporte_autorizado = transporte_autorizado
            existente.publicacion_trabajos = publicacion_trabajos
            existente.actualizado_en = datetime.utcnow()
            existente.actualizado_por_id = actualizado_por_id
            return await self.consentimientos_repo.actualizar(alumno_id, existente)

        consentimiento = ConsentimientoEntidad(
            alumno_id=alumno_id,
            uso_imagen=uso_imagen,
            actividades_externas=actividades_externas,
            atencion_medica_emergencia=atencion_medica_emergencia,
            transporte_autorizado=transporte_autorizado,
            publicacion_trabajos=publicacion_trabajos,
            creado_en=datetime.utcnow(),
            actualizado_en=datetime.utcnow(),
            actualizado_por_id=actualizado_por_id,
        )
        return await self.consentimientos_repo.crear(consentimiento)
