# app/kernel/application/cursosextra/alumno_externo/obtener_alumno_externo.py

"""
Caso de Uso: Obtener Alumno Externo por ID
"""
from app.kernel.domain.cursos_extra import (
    AlumnoExterno,
    AlumnoExternoRepositoryPort,
    AlumnoExternoNoEncontrado,
)


class ObtenerAlumnoExterno:
    """
    Caso de Uso: Obtener un alumno externo por su ID.
    """
    
    def __init__(self, alumno_externo_repo: AlumnoExternoRepositoryPort):
        self.alumno_externo_repo = alumno_externo_repo
    
    async def execute(self, alumno_id: int) -> AlumnoExterno:
        """Ejecuta el caso de uso."""
        
        alumno = await self.alumno_externo_repo.obtener_por_id(alumno_id)
        if not alumno:
            raise AlumnoExternoNoEncontrado(alumno_id)
        
        return alumno
