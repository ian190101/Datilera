# app/kernel/application/cursosextra/alumno_externo/buscar_alumnos_externos.py

"""
Caso de Uso: Buscar Alumnos Externos
"""
from typing import List, Optional

from app.kernel.domain.cursos_extra import (
    AlumnoExterno,
    AlumnoExternoRepositoryPort,
)


class BuscarAlumnosExternosDTO:
    """DTO de entrada para buscar alumnos externos."""
    def __init__(
        self,
        termino_busqueda: str,
        tipo_busqueda: str = "nombre",  # "nombre" o "celular"
        sede_id: Optional[int] = None,
        limite: int = 20,
    ):
        self.termino_busqueda = termino_busqueda
        self.tipo_busqueda = tipo_busqueda
        self.sede_id = sede_id
        self.limite = limite


class BuscarAlumnosExternos:
    """
    Caso de Uso: Buscar alumnos externos por nombre o celular del tutor.
    """
    
    def __init__(self, alumno_externo_repo: AlumnoExternoRepositoryPort):
        self.alumno_externo_repo = alumno_externo_repo
    
    async def execute(self, dto: BuscarAlumnosExternosDTO) -> List[AlumnoExterno]:
        """Ejecuta el caso de uso."""
        
        if dto.tipo_busqueda == "celular":
            return await self.alumno_externo_repo.buscar_por_celular_tutor(
                celular=dto.termino_busqueda,
                sede_id=dto.sede_id
            )
        else:
            return await self.alumno_externo_repo.buscar_por_nombre(
                nombre=dto.termino_busqueda,
                sede_id=dto.sede_id,
                limite=dto.limite
            )
