#app/kernel/application/academico/horarios_paralelos/listar_horarios_paralelos.py
"""Caso de uso: Listar horarios paralelos."""
from typing import Sequence
from app.kernel.domain.academico.horarios_paralelos_entidad import HorarioParalelo
from app.kernel.domain.academico.ports import IHorarioParaleloRepository

class ListarHorariosParalelos:
    """Caso de uso: Listar asignaciones de horarios a paralelos."""
    
    def __init__(self, horario_paralelo_repo: IHorarioParaleloRepository):
        self.horario_paralelo_repo = horario_paralelo_repo
    
    async def execute(
        self,
        paralelo_id: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[HorarioParalelo]:
        """
        Lista asignaciones de horarios, filtrando por paralelo si se proporciona.
        
        Args:
            paralelo_id: ID del paralelo para filtrar (opcional)
            limit: Límite de resultados
            offset: Offset para paginación
        
        Returns:
            Lista de asignaciones
        """
        if paralelo_id:
            hp_orm = await self.horario_paralelo_repo.list_by_paralelo(paralelo_id)
        else:
            hp_orm = await self.horario_paralelo_repo.list(limit=limit, offset=offset)
        return [HorarioParalelo.model_validate(hp) for hp in hp_orm]