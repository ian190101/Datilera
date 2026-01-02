# app/kernel/application/calendario/eventos/listar_eventos_por_fecha.py

from datetime import date
from typing import List, Optional

from app.kernel.domain.calendario import (
    EventoCalendario,
    EventoCalendarioRepositoryPort,
)


class ListarEventosPorFechaUseCase:
    """Caso de uso: Listar eventos de una fecha específica."""
    
    def __init__(self, evento_repo: EventoCalendarioRepositoryPort):
        self.evento_repo = evento_repo
    
    async def ejecutar(
        self,
        fecha: date,
        sede_id: Optional[int] = None,
        solo_aprobados: bool = True,
    ) -> List[EventoCalendario]:
        """Lista eventos de una fecha específica.
        
        Args:
            fecha: Fecha a consultar
            sede_id: Filtrar por sede (opcional)
            solo_aprobados: Solo eventos aprobados
            
        Returns:
            Lista de EventoCalendario de esa fecha
        """
        return await self.evento_repo.listar(
            sede_id=sede_id,
            fecha_inicio=fecha,
            fecha_fin=fecha,
            aprobado=True if solo_aprobados else None,
        )
