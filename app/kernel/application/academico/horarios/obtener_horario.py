#app/kernel/application/academico/horarios/obtener_horario.py
"""Caso de uso: Obtener un horario por ID."""
from app.kernel.domain.academico.horarios_entidad import Horario
from app.kernel.domain.academico.ports import IHorarioRepository
from app.kernel.domain.academico.errors import HorarioNoEncontrado

class ObtenerHorario:
    def __init__(self, horario_repo: IHorarioRepository):
        self.horario_repo = horario_repo

    async def execute(self, horario_id: int) -> Horario:
        """
        Obtiene un horario por su ID.
        
        Args:
            horario_id: ID del horario
        
        Returns:
            Horario encontrado
        
        Raises:
            HorarioNoEncontrado: Si el horario no existe
        """
        horario = await self.horario_repo.get(horario_id)
    
        if not horario:
            raise HorarioNoEncontrado(f"Horario con ID {horario_id} no encontrado")
    
        return Horario.model_validate(horario)