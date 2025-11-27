from typing import Optional
from datetime import datetime, date

from app.kernel.domain.alumnos.alumno_hermano_entidad import AlumnoHermanoEntidad
from app.kernel.domain.alumnos.ports import AlumnosHermanosRepositoryPort
from app.kernel.domain.alumnos.errors import HermanoNoEncontradoError


class ActualizarHermanoCU:
    """Actualizar datos de un hermano."""

    def __init__(self, hermanos_repo: AlumnosHermanosRepositoryPort):
        self.hermanos_repo = hermanos_repo

    async def ejecutar(
        self,
        hermano_id: int,
        nombres: Optional[str] = None,
        apellidos: Optional[str] = None,
        fecha_nacimiento: Optional[date] = None,
        genero: Optional[str] = None,
        estudia_en_jardin: Optional[bool] = None,
        lugar_ocupa: Optional[int] = None,
    ) -> AlumnoHermanoEntidad:
        hermano = await self.hermanos_repo.obtener_por_id(hermano_id)
        if not hermano:
            raise HermanoNoEncontradoError(hermano_id=hermano_id)

        data = hermano.model_dump()
        if nombres is not None:
            data["nombres"] = nombres.strip()
        if apellidos is not None:
            data["apellidos"] = apellidos.strip()
        if fecha_nacimiento is not None:
            data["fecha_nacimiento"] = fecha_nacimiento
        if genero is not None:
            data["genero"] = genero
        if estudia_en_jardin is not None:
            data["estudia_en_jardin"] = estudia_en_jardin
        if lugar_ocupa is not None:
            data["lugar_ocupa"] = lugar_ocupa

        data["creado_en"] = hermano.creado_en or datetime.utcnow()
        actualizado = AlumnoHermanoEntidad(**data)
        return await self.hermanos_repo.actualizar(hermano_id, actualizado)
