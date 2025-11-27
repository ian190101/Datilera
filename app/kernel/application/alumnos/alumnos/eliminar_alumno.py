# app/application/alumnos/alumnos/eliminar_alumno.py

from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort
from app.kernel.domain.alumnos.errors import AlumnoNoEncontradoError


class EliminarAlumnoCU:
    """Caso de uso: Eliminar (soft delete) un alumno"""

    def __init__(self, alumno_repo: AlumnoRepositoryPort):
        self.alumno_repo = alumno_repo

    async def ejecutar(self, alumno_id: int) -> bool:
        """
        Eliminar alumno (marcarlo como inactivo)
        
        Args:
            alumno_id: ID del alumno a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            AlumnoNoEncontradoError: Si el alumno no existe
        """
        
        # Verificar que existe
        alumno = await self.alumno_repo.obtener_por_id(alumno_id)
        if not alumno:
            raise AlumnoNoEncontradoError(alumno_id=alumno_id)
        
        # Eliminar (soft delete - marca como inactivo)
        return await self.alumno_repo.eliminar(alumno_id)
