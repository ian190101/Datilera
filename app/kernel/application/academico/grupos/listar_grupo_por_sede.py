# app/kernel/application/academico/grupos/listar_grupos_por_sede.py
from typing import Sequence
from app.kernel.domain.academico.grupos_entidad import Grupo
from app.kernel.domain.academico.ports import IGrupoRepository

class ListarGruposPorSede:
    """Caso de uso: Listar grupos de una sede."""
    
    def __init__(self, grupo_repo: IGrupoRepository):
        self.grupo_repo = grupo_repo
    
    async def execute(
        self,
        sede_id: int,
        gestion: int | None = None,
        solo_activos: bool = False,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Sequence[Grupo]:
        """
        Lista los grupos de una sede, admitiendo filtros combinables.
        """
        if sede_id <= 0:
            raise ValueError("sede_id debe ser un entero positivo")
        if gestion is not None and gestion < 2000:
            raise ValueError("gestion inválida")

        grupos = await self.grupo_repo.list_by_sede(
            sede_id=sede_id,
            gestion=gestion,
            solo_activos=solo_activos,
            limit=limit,
            offset=offset,
        )
        return [Grupo.model_validate(g) for g in grupos]