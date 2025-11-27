from typing import Optional
from datetime import datetime

from app.kernel.domain.alumnos.alumno_tutor_entidad import AlumnoTutorEntidad
from app.kernel.domain.alumnos.ports import AlumnoTutorRepositoryPort
from app.kernel.domain.alumnos.errors import (
    RelacionAlumnoTutorNoEncontradaError,
    TutorPrincipalDuplicadoError,
)


class ActualizarRelacionTutorCU:
    """Actualizar relación alumno-tutor."""

    def __init__(self, relacion_repo: AlumnoTutorRepositoryPort):
        self.relacion_repo = relacion_repo

    async def ejecutar(
        self,
        relacion_id: int,
        relacion: Optional[str] = None,
        es_principal: Optional[bool] = None,
        vive_con_alumno: Optional[bool] = None,
        prioridad_contacto: Optional[int] = None,
    ) -> AlumnoTutorEntidad:
        actual = await self.relacion_repo.obtener_por_id(relacion_id)
        if not actual:
            raise RelacionAlumnoTutorNoEncontradaError()

        data = actual.model_dump()

        if relacion is not None:
            data["relacion"] = relacion
        if vive_con_alumno is not None:
            data["vive_con_alumno"] = vive_con_alumno
        if prioridad_contacto is not None:
            data["prioridad_contacto"] = prioridad_contacto

        # Manejo de tutor principal
        if es_principal is not None and es_principal != actual.es_principal:
            if es_principal:
                existente_principal = await self.relacion_repo.obtener_tutor_principal(
                    actual.alumno_id
                )
                if existente_principal and existente_principal.id != relacion_id:
                    raise TutorPrincipalDuplicadoError(actual.alumno_id)
            data["es_principal"] = es_principal

        data["actualizado_en"] = datetime.utcnow()
        actualizado = AlumnoTutorEntidad(**data)
        return await self.relacion_repo.actualizar(relacion_id, actualizado)
