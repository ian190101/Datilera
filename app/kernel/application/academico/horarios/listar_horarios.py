# app/kernel/application/academico/horarios/listar_horarios.py
"""Caso de uso: Listar todos los horarios."""
from typing import Sequence
from app.kernel.domain.academico.horarios_entidad import Horario
from app.kernel.domain.academico.ports import IHorarioRepository



class ListarHorarios:
    """Caso de uso: Listar todos los horarios ordenados."""
    
    def __init__(self, horario_repo: IHorarioRepository):
        self.horario_repo = horario_repo
    
    async def execute(self) -> Sequence[Horario]:
        """
        Lista todos los horarios ordenados por hora de inicio.
        
        Returns:
            Lista de horarios
        """
        horarios_orm = await self.horario_repo.list()
        return [Horario.model_validate(h) for h in horarios_orm]