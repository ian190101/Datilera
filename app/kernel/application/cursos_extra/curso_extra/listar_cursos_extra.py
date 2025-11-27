# app/kernel/application/cursosextra/curso_extra/listar_cursos_extra.py

"""
Caso de Uso: Listar Cursos Extra
"""
from typing import List, Optional

from app.kernel.domain.cursos_extra import (
    CursoExtra,
    CursoExtraRepositoryPort,
)


class ListarCursosExtraDTO:
    """DTO de entrada para listar cursos."""
    def __init__(
        self,
        sede_id: int,
        activo: Optional[bool] = None,
        gestion: Optional[int] = None,
        solo_con_cupos: bool = False,
        limite: int = 100,
        offset: int = 0,
    ):
        self.sede_id = sede_id
        self.activo = activo
        self.gestion = gestion
        self.solo_con_cupos = solo_con_cupos
        self.limite = limite
        self.offset = offset


class ListarCursosExtra:
    """
    Caso de Uso: Listar cursos extra con filtros.
    
    Filtros disponibles:
    - Por sede (obligatorio)
    - Por estado activo/inactivo
    - Por gestión/año
    - Solo cursos con cupos disponibles
    """
    
    def __init__(self, curso_repo: CursoExtraRepositoryPort):
        self.curso_repo = curso_repo
    
    async def execute(self, dto: ListarCursosExtraDTO) -> List[CursoExtra]:
        """Ejecuta el caso de uso."""
        
        if dto.solo_con_cupos:
            # Filtro especial: solo cursos activos con cupos
            return await self.curso_repo.obtener_activos_con_cupos(dto.sede_id)
        
        # Listado general con filtros
        return await self.curso_repo.obtener_por_sede(
            sede_id=dto.sede_id,
            activo=dto.activo,
            gestion=dto.gestion,
            limite=dto.limite,
            offset=dto.offset,
        )
