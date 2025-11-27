from datetime import datetime, time, date
from typing import Optional

from app.kernel.domain.alumnos.asistencia_personal_entidad import AsistenciaPersonalEntidad
from app.kernel.domain.alumnos.ports import AsistenciaPersonalRepositoryPort
from app.kernel.domain.alumnos.errors import AsistenciaNoEncontradaError


class RegistrarSalidaPersonalCU:
    """Registrar salida de personal."""

    def __init__(self, asistencia_repo: AsistenciaPersonalRepositoryPort):
        self.asistencia_repo = asistencia_repo

    async def ejecutar(
        self,
        personal_id: int,
        fecha: Optional[date] = None,
        hora_salida: Optional[time] = None,
        observaciones: Optional[str] = None,
    ) -> AsistenciaPersonalEntidad:
        fecha = fecha or date.today()
        asistencia = await self.asistencia_repo.obtener_por_personal_fecha(personal_id, fecha)
        if not asistencia:
            raise AsistenciaNoEncontradaError()

        data = asistencia.model_dump()
        data["hora_salida"] = hora_salida or datetime.utcnow().time()
        if observaciones is not None:
            data["observaciones"] = observaciones
        actualizado = AsistenciaPersonalEntidad(**data)
        return await self.asistencia_repo.actualizar(asistencia.id, actualizado)
