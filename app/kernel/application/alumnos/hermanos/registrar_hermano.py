from datetime import datetime
from typing import Optional, List

from app.kernel.domain.alumnos.alumno_hermano_entidad import AlumnoHermanoEntidad
from app.kernel.domain.alumnos.ports import (
    AlumnoRepositoryPort,
    AlumnosHermanosRepositoryPort,
)
from app.kernel.domain.alumnos.errors import AlumnoNoEncontradoError


class RegistrarHermanoCU:
    """Registrar un hermano para un alumno."""

    def __init__(
        self,
        alumno_repo: AlumnoRepositoryPort,
        hermanos_repo: AlumnosHermanosRepositoryPort,
    ):
        self.alumno_repo = alumno_repo
        self.hermanos_repo = hermanos_repo

    async def ejecutar(
        self,
        alumno_id: int,
        nombres: str,
        apellidos: str,
        fecha_nacimiento: Optional[datetime.date] = None,
        genero: Optional[str] = None,
        estudia_en_jardin: bool = False,
        lugar_ocupa: Optional[int] = None,
    ) -> AlumnoHermanoEntidad:
        alumno = await self.alumno_repo.obtener_por_id(alumno_id)
        if not alumno:
            raise AlumnoNoEncontradoError(alumno_id=alumno_id)

        hermanos_actuales: List[AlumnoHermanoEntidad] = await self.hermanos_repo.listar_por_alumno(
            alumno_id
        )
        if lugar_ocupa is None:
            lugar_ocupa = len(hermanos_actuales) + 1

        hermano = AlumnoHermanoEntidad(
            alumno_id=alumno_id,
            nombres=nombres.strip(),
            apellidos=apellidos.strip(),
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            estudia_en_jardin=estudia_en_jardin,
            lugar_ocupa=lugar_ocupa,
            creado_en=datetime.utcnow(),
        )
        return await self.hermanos_repo.crear(hermano)
