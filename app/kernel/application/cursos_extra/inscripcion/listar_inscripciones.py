# app/kernel/application/cursosextra/inscripcion/listar_inscripciones.py

"""
Caso de Uso: Listar Inscripciones
"""
from typing import List, Optional

from app.kernel.domain.cursos_extra import (
    InscripcionCursoExtra,
    EstadoInscripcionCursoExtra,
    InscripcionCursoExtraRepositoryPort,
)


class ListarInscripcionesDTO:
    """DTO de entrada para listar inscripciones."""
    def __init__(
        self,
        curso_id: int,
        estado: Optional[EstadoInscripcionCursoExtra] = None,
        limite: int = 100,
        offset: int = 0,
    ):
        self.curso_id = curso_id
        self.estado = estado
        self.limite = limite
        self.offset = offset


class ListarInscripciones:
    """
    Caso de Uso: Listar inscripciones de un curso con filtros.
    """
    
    def __init__(self, inscripcion_repo: InscripcionCursoExtraRepositoryPort):
        self.inscripcion_repo = inscripcion_repo
    
    async def execute(self, dto: ListarInscripcionesDTO) -> List[InscripcionCursoExtra]:
        """Ejecuta el caso de uso."""
        
        return await self.inscripcion_repo.obtener_por_curso(
            curso_id=dto.curso_id,
            estado=dto.estado,
            limite=dto.limite,
            offset=dto.offset,
        )
