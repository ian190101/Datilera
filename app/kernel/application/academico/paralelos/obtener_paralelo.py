#app/kernel/application/academico/paralelos/obtener_paralelo.py
"""Caso de uso: Obtener un paralelo por ID."""
from app.kernel.domain.academico.paralelos_entidad import Paralelo
from app.kernel.domain.academico.ports import IParaleloRepository
from app.kernel.domain.academico.errors import ParaleloNoEncontrado

class ObtenerParalelo:
    def __init__(self, paralelo_repo: IParaleloRepository):
        self.paralelo_repo = paralelo_repo

    async def execute(self, paralelo_id: int) -> Paralelo:
        """
        Obtiene un paralelo por su ID.
        
        Args:
            paralelo_id: ID del paralelo
        
        Returns:
            Paralelo encontrado
        
        Raises:
            ParaleloNoEncontrado: Si el paralelo no existe
        """
        paralelo = await self.paralelo_repo.get(paralelo_id)
        if not paralelo:
            raise ParaleloNoEncontrado(f"Paralelo con ID {paralelo_id} no encontrado")
        return Paralelo.model_validate(paralelo)