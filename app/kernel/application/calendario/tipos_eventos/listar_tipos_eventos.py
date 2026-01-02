# app/kernel/application/calendario/tipos_eventos/listar_tipos_eventos.py

from typing import List, Optional

from app.kernel.domain.calendario import (
    TipoEvento,
    TipoEventoRepositoryPort,
)


class ListarTiposEventosUseCase:
    """Caso de uso: Listar tipos de eventos (US-CAL-001).
    
    Reglas:
    - Filtrar por sede
    - Filtrar por estado activo/inactivo
    - Ordenados alfabéticamente
    """
    
    def __init__(self, tipo_evento_repo: TipoEventoRepositoryPort):
        self.tipo_evento_repo = tipo_evento_repo
    
    async def ejecutar(
        self,
        sede_id: Optional[int] = None,
        activo: Optional[bool] = None,
        solo_visibles_profesoras: bool = False,
        solo_visibles_tutores: bool = False,
    ) -> List[TipoEvento]:
        """Lista tipos de eventos con filtros.
        
        Args:
            sede_id: Filtrar por sede (opcional)
            activo: Filtrar por estado (opcional)
            solo_visibles_profesoras: Solo visibles para profesoras
            solo_visibles_tutores: Solo visibles para tutores
            
        Returns:
            Lista de TipoEvento
        """
        tipos = await self.tipo_evento_repo.listar(
            sede_id=sede_id,
            activo=activo,
        )
        
        # Aplicar filtros adicionales
        if solo_visibles_profesoras:
            tipos = [t for t in tipos if t.visible_profesoras]
        
        if solo_visibles_tutores:
            tipos = [t for t in tipos if t.visible_tutores]
        
        return tipos
