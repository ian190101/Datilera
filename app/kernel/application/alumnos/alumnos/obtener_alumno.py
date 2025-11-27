# app/application/alumnos/alumnos/obtener_alumno_cu.py

from typing import Optional

from app.kernel.domain.alumnos.alumno_entidad import AlumnoEntidad
from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort
from app.kernel.domain.alumnos.errors import AlumnoNoEncontradoError


class ObtenerAlumnoCU:
    """Caso de uso: Obtener alumno por ID, código o documento"""

    def __init__(self, alumno_repo: AlumnoRepositoryPort):
        self.alumno_repo = alumno_repo

    async def por_id(self, alumno_id: int) -> AlumnoEntidad:
        """Obtener alumno por ID"""
        alumno = await self.alumno_repo.obtener_por_id(alumno_id)
        if not alumno:
            raise AlumnoNoEncontradoError(alumno_id=alumno_id)
        return alumno

    async def por_codigo(self, codigo: str) -> AlumnoEntidad:
        """Obtener alumno por código único"""
        alumno = await self.alumno_repo.obtener_por_codigo(codigo)
        if not alumno:
            raise AlumnoNoEncontradoError(codigo=codigo)
        return alumno

    async def por_documento(self, numero_documento: str) -> AlumnoEntidad:
        """Obtener alumno por número de documento"""
        alumno = await self.alumno_repo.obtener_por_documento(numero_documento)
        if not alumno:
            raise AlumnoNoEncontradoError(documento=numero_documento)
        return alumno
