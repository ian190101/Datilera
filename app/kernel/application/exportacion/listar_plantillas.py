# app/kernel/application/exportacion/listar_plantillas.py

from __future__ import annotations
from typing import Optional

from pydantic import BaseModel

from app.kernel.domain.exportacion import (
    AbstractPlantillaExportacionRepository,
    PlantillaExportacion,
    TipoReporte,
)


class ListarPlantillasIn(BaseModel):
    """Input para listar plantillas."""
    tipo_reporte: Optional[TipoReporte] = None
    solo_publicas: bool = True


class ListarPlantillasOut(BaseModel):
    """Output con lista de plantillas."""
    plantillas: list[PlantillaExportacion]
    total: int


class ListarPlantillasCU:
    """
    Caso de uso: Listar plantillas de exportación disponibles.
    
    Retorna:
    - Plantillas públicas del sistema
    - Plantillas privadas del usuario actual (si solo_publicas=False)
    
    Filtros opcionales por tipo de reporte.
    """
    
    def __init__(
        self,
        plantilla_repo: AbstractPlantillaExportacionRepository,
        usuario_id: Optional[int] = None,
    ) -> None:
        self._repo = plantilla_repo
        self._usuario_id = usuario_id
    
    async def __call__(
        self,
        data: ListarPlantillasIn,
    ) -> ListarPlantillasOut:
        """Lista plantillas según filtros."""
        
        plantillas = await self._repo.listar_plantillas(
            tipo_reporte=data.tipo_reporte,
            solo_publicas=data.solo_publicas,
            usuario_id=self._usuario_id if not data.solo_publicas else None,
        )
        
        return ListarPlantillasOut(
            plantillas=plantillas,
            total=len(plantillas),
        )
