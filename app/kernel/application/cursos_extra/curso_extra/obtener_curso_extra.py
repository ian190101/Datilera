# app/kernel/application/cursosextra/curso_extra/obtener_curso_extra.py

"""
Caso de Uso: Obtener Curso Extra por ID
"""
from app.kernel.domain.cursos_extra import (
    CursoExtra,
    CursoExtraRepositoryPort,
    CursoExtraNoEncontrado,
)


class ObtenerCursoExtra:
    """
    Caso de Uso: Obtener un curso extra por su ID.
    """
    
    def __init__(self, curso_repo: CursoExtraRepositoryPort):
        self.curso_repo = curso_repo
    
    async def execute(self, curso_id: int) -> CursoExtra:
        """Ejecuta el caso de uso."""
        
        curso = await self.curso_repo.obtener_por_id(curso_id)
        if not curso:
            raise CursoExtraNoEncontrado(curso_id)
        
        return curso
