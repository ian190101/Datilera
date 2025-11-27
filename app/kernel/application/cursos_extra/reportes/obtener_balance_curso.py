# app/kernel/application/cursosextra/reportes/obtener_balance_curso.py

"""
Caso de Uso: Obtener Balance Consolidado de Curso
"""
from typing import Dict

from app.kernel.domain.cursos_extra import (
    IngresoCursoExtraRepositoryPort,
    CursoExtraRepositoryPort,
    CursoExtraNoEncontrado,
)


class ObtenerBalanceCurso:
    """
    Caso de Uso: Obtener el balance consolidado de un curso.
    
    Retorna el estado financiero completo del registro de ingresos.
    """
    
    def __init__(
        self,
        ingreso_repo: IngresoCursoExtraRepositoryPort,
        curso_repo: CursoExtraRepositoryPort,
    ):
        self.ingreso_repo = ingreso_repo
        self.curso_repo = curso_repo
    
    async def execute(self, curso_id: int) -> Dict:
        """Ejecuta el caso de uso."""
        
        # Validar que el curso existe
        curso = await self.curso_repo.obtener_por_id(curso_id)
        if not curso:
            raise CursoExtraNoEncontrado(curso_id)
        
        # Obtener balance consolidado
        balance = await self.ingreso_repo.obtener_balance_curso(curso_id)
        
        return balance
