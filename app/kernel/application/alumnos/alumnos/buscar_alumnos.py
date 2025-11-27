# app/application/alumnos/alumnos/buscar_alumnos.py

from typing import List, Optional

from app.kernel.domain.alumnos.alumno_entidad import AlumnoEntidad
from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort


class BuscarAlumnosCU:
    """Caso de uso: Buscar alumnos por diferentes criterios"""

    def __init__(self, alumno_repo: AlumnoRepositoryPort):
        self.alumno_repo = alumno_repo

    async def ejecutar(
        self, 
        termino: str, 
        sede_id: Optional[int] = None
    ) -> List[AlumnoEntidad]:
        """
        Buscar alumnos por nombre o documento
        
        Args:
            termino: Texto a buscar (nombre, apellido o documento)
            sede_id: Filtrar por sede (opcional)
            
        Returns:
            Lista de alumnos que coinciden
        """
        return await self.alumno_repo.buscar(termino.strip(), sede_id)
