# app/kernel/application/academico/paralelos/listar_paralelos_por_grupo.py
"""Caso de uso: Listar paralelos de un grupo (con filtros)."""
from typing import Sequence
from app.kernel.domain.academico.paralelos_entidad import Paralelo
from app.kernel.domain.academico.ports import IParaleloRepository


class ListarParalelosPorGrupo:
    """Caso de uso: Listar paralelos de un grupo."""

    def __init__(self, paralelo_repo: IParaleloRepository):
        self.paralelo_repo = paralelo_repo

    async def execute(
        self,
        grupo_id: int,
        *,
        solo_activos: bool = False,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str = "nombre",  # o "id" según tu dominio
    ) -> Sequence[Paralelo]:
        """
        Lista los paralelos de un grupo con opciones de filtro y paginación.

        Args:
            grupo_id: ID del grupo
            solo_activos: Si True, retorna solo paralelos activos
            limit: Máximo de registros
            offset: Desplazamiento para paginación
            order_by: Campo de orden ("nombre" o "id")

        Returns:
            Lista de paralelos
        """
        if grupo_id <= 0:
            raise ValueError("grupo_id debe ser un entero positivo")
        if limit is not None and limit <= 0:
            raise ValueError("limit debe ser > 0")
        if offset is not None and offset < 0:
            raise ValueError("offset no puede ser negativo")

        paralelos = await self.paralelo_repo.list_by_grupo(
            grupo_id=grupo_id,
            solo_activos=solo_activos,
            limit=limit,
            offset=offset,
            order_by=order_by,
        )
        return [Paralelo.model_validate(p) for p in paralelos]