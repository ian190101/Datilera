# app/kernel/application/academico/grupos/eliminar_grupo.py
"""Caso de uso: Eliminar (desactivar) un grupo (soft delete)."""

from app.kernel.domain.academico.ports import IGrupoRepository, IParaleloRepository
from app.kernel.domain.academico.errors import GrupoNoEncontrado, GrupoEnUso


class EliminarGrupo:
    """Caso de uso: Desactivar un grupo (soft delete)."""

    def __init__(
        self,
        grupo_repo: IGrupoRepository,
        paralelo_repo: IParaleloRepository,
    ):
        self.grupo_repo = grupo_repo
        self.paralelo_repo = paralelo_repo

    async def execute(self, grupo_id: int) -> None:
        """
        Desactiva un grupo si no tiene paralelos asociados.

        Args:
            grupo_id: ID del grupo a desactivar

        Raises:
            GrupoNoEncontrado: Si el grupo no existe
            GrupoEnUso: Si el grupo tiene paralelos asociados
        """
        # 1) Verificar existencia
        grupo = await self.grupo_repo.get(grupo_id)
        if not grupo:
            raise GrupoNoEncontrado(f"Grupo con ID {grupo_id} no encontrado")

        # 2) Verificar que no tenga paralelos
        # Mejor usar exists/count para no cargar todos:
        # existe = await self.paralelo_repo.exists_by_grupo(grupo_id)
        # if existe: ...
        paralelos = await self.paralelo_repo.list_by_grupo(grupo_id)
        if paralelos:
            # Si 'grupo' es dict:
            letra = grupo.get("letra") or f"ID {grupo_id}"
            raise GrupoEnUso(
                f"El grupo '{letra}' tiene {len(paralelos)} paralelo(s) asociado(s)"
            )

        # 3) Soft delete (desactivar)
        await self.grupo_repo.soft_delete(grupo_id)