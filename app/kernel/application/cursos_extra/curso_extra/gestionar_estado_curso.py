# app/kernel/application/cursosextra/curso_extra/gestionar_estado_curso.py

"""
Caso de Uso: Gestionar Estado del Curso (Activar/Desactivar)
"""
from app.kernel.domain.cursos_extra import (
    CursoExtra,
    CursoExtraRepositoryPort,
    CursoExtraNoEncontrado,
)


class GestionarEstadoCurso:
    """
    Caso de Uso: Activar o desactivar un curso extra.
    
    Reglas:
    - Solo cambia el estado, no afecta inscripciones existentes
    - Un curso desactivado no permite nuevas inscripciones
    """
    
    def __init__(self, curso_repo: CursoExtraRepositoryPort):
        self.curso_repo = curso_repo
    
    async def activar(self, curso_id: int) -> CursoExtra:
        """Activa un curso."""
        curso = await self.curso_repo.obtener_por_id(curso_id)
        if not curso:
            raise CursoExtraNoEncontrado(curso_id)
        
        return await self.curso_repo.activar_desactivar(curso_id, True)
    
    async def desactivar(self, curso_id: int) -> CursoExtra:
        """Desactiva un curso."""
        curso = await self.curso_repo.obtener_por_id(curso_id)
        if not curso:
            raise CursoExtraNoEncontrado(curso_id)
        
        return await self.curso_repo.activar_desactivar(curso_id, False)
