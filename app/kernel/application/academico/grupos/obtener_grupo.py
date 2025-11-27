#app/kernel/application/academico/grupos/obtener_grupo.py
"""Caso de uso: Obtener un grupo por ID."""
from app.kernel.domain.academico.grupos_entidad import Grupo
from app.kernel.domain.academico.ports import IGrupoRepository
from app.kernel.domain.academico.errors import GrupoNoEncontrado

class ObtenerGrupo:
    def __init__(self, grupo_repo: IGrupoRepository):
        self.grupo_repo = grupo_repo

    async def execute(self, grupo_id: int) -> Grupo:
        """
        Obtiene un grupo por su ID.
        
        Args:
            grupo_id: ID del grupo
        
        Returns:
            Grupo encontrado
        
        Raises:
            GrupoNoEncontrado: Si el grupo no existe
        """
        grupo = await self.grupo_repo.get(grupo_id)
        if not grupo:
            raise GrupoNoEncontrado(f"Grupo con ID {grupo_id} no encontrado")
        return Grupo.model_validate(grupo)