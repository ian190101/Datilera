# app/kernel/application/cursosextra/categoria_costo/listar_categorias_costo.py

"""
Caso de Uso: Listar Categorías de Costo
"""
from typing import List, Optional

from app.kernel.domain.cursos_extra import (
    CategoriaCostoCursoExtra,
    CategoriaCostoCursoExtraRepositoryPort,
)


class ListarCategoriasCostoDTO:
    """DTO de entrada para listar categorías."""
    def __init__(
        self,
        curso_id: int,
        activo: Optional[bool] = None,
    ):
        self.curso_id = curso_id
        self.activo = activo


class ListarCategoriasCosto:
    """
    Caso de Uso: Listar categorías de costo de un curso.
    """
    
    def __init__(self, categoria_repo: CategoriaCostoCursoExtraRepositoryPort):
        self.categoria_repo = categoria_repo
    
    async def execute(self, dto: ListarCategoriasCostoDTO) -> List[CategoriaCostoCursoExtra]:
        """Ejecuta el caso de uso."""
        
        return await self.categoria_repo.listar_por_curso(
            curso_id=dto.curso_id,
            activo=dto.activo
        )
