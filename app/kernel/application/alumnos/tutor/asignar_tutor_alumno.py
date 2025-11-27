from typing import Optional
from datetime import datetime

from app.kernel.domain.alumnos.alumno_tutor_entidad import AlumnoTutorEntidad
from app.kernel.domain.alumnos.ports import (
    AlumnoRepositoryPort,
    TutorRepositoryPort,
    AlumnoTutorRepositoryPort,
)
from app.kernel.domain.alumnos.errors import (
    AlumnoNoEncontradoError,
    TutorNoEncontradoError,
    RelacionAlumnoTutorDuplicadaError,
    TutorPrincipalDuplicadoError,
)


class AsignarTutorAlumnoCU:
    """Asignar un tutor a un alumno (y opcionalmente como principal)."""

    def __init__(
        self,
        alumno_repo: AlumnoRepositoryPort,
        tutor_repo: TutorRepositoryPort,
        relacion_repo: AlumnoTutorRepositoryPort,
    ):
        self.alumno_repo = alumno_repo
        self.tutor_repo = tutor_repo
        self.relacion_repo = relacion_repo

    async def ejecutar(
        self,
        alumno_id: int,
        tutor_id: int,
        relacion: str,
        es_principal: bool = False,
        vive_con_alumno: bool = False,
        prioridad_contacto: int = 1,
    ) -> AlumnoTutorEntidad:
        alumno = await self.alumno_repo.obtener_por_id(alumno_id)
        if not alumno:
            raise AlumnoNoEncontradoError(alumno_id=alumno_id)

        tutor = await self.tutor_repo.obtener_por_id(tutor_id)
        if not tutor:
            raise TutorNoEncontradoError(tutor_id=tutor_id)

        # Verificar duplicado
        existentes = await self.relacion_repo.listar_por_alumno(alumno_id)
        for r in existentes:
            if r.tutor_id == tutor_id:
                raise RelacionAlumnoTutorDuplicadaError(alumno_id, tutor_id)

        # Verificar tutor principal
        if es_principal:
            principal = await self.relacion_repo.obtener_tutor_principal(alumno_id)
            if principal:
                raise TutorPrincipalDuplicadoError(alumno_id)

        relacion_entidad = AlumnoTutorEntidad(
            alumno_id=alumno_id,
            tutor_id=tutor_id,
            relacion=relacion,
            es_principal=es_principal,
            vive_con_alumno=vive_con_alumno,
            prioridad_contacto=prioridad_contacto,
            creado_en=datetime.utcnow(),
        )
        return await self.relacion_repo.crear(relacion_entidad)
