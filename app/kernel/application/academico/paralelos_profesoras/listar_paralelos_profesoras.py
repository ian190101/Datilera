#app/kernel/application/academico/paralelos_profesoras/listar_paralelos_profesoras.py
"""Caso de uso: Listar paralelos profesoras."""
from typing import Sequence
from app.kernel.domain.academico.paralelos_profesoras_entidad import ParaleloProfesora
from app.kernel.domain.academico.ports import IParaleloProfesorRepository  # Usar interface genérica

class ListarParalelosProfesoras:
    """Caso de uso: Listar asignaciones de profesoras a paralelos."""
    
    def __init__(self, paralelo_profesora_repo: IParaleloProfesorRepository):
        self.paralelo_profesora_repo = paralelo_profesora_repo
    
    async def execute(
        self,
        paralelo_id: int | None = None,
        profesora_id: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[ParaleloProfesora]:
        """
        Lista asignaciones, filtrando por paralelo o profesora si se proporciona.
        
        Args:
            paralelo_id: ID del paralelo para filtrar (opcional)
            profesora_id: ID de la profesora para filtrar (opcional)
            limit: Límite de resultados
            offset: Offset para paginación
        
        Returns:
            Lista de asignaciones
        """
        if paralelo_id:
            pp_orm = await self.paralelo_profesora_repo.list_by_paralelo(paralelo_id)
        elif profesora_id:
            pp_orm = await self.paralelo_profesora_repo.list_by_profesor(profesora_id)
        else:
            pp_orm = await self.paralelo_profesora_repo.list(limit=limit, offset=offset)
        return [ParaleloProfesora.model_validate(pp) for pp in pp_orm]