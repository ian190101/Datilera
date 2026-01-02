# app/kernel/application/calendario/eventos/listar_eventos.py

from datetime import date
from typing import List, Optional

from app.kernel.domain.calendario import (
    EventoCalendario,
    EventoCalendarioRepositoryPort,
)


class ListarEventosUseCase:
    """Caso de uso: Listar eventos con filtros (US-CAL-002).
    
    Reglas:
    - Filtrar por sede, fechas, tipo
    - Ordenados por fecha
    - Paginación
    """
    
    def __init__(self, evento_repo: EventoCalendarioRepositoryPort):
        self.evento_repo = evento_repo
    
    async def ejecutar(
        self,
        sede_id: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        tipo_evento_id: Optional[int] = None,
        aprobado: Optional[bool] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> List[EventoCalendario]:
        """Lista eventos con filtros.
        
        Args:
            sede_id: Filtrar por sede
            fecha_inicio: Fecha inicio del rango
            fecha_fin: Fecha fin del rango
            tipo_evento_id: Filtrar por tipo
            aprobado: Filtrar por estado de aprobación
            limite: Máximo de resultados
            offset: Saltar registros
            
        Returns:
            Lista de EventoCalendario
        """
        return await self.evento_repo.listar(
            sede_id=sede_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            tipo_evento_id=tipo_evento_id,
            aprobado=aprobado,
            limite=limite,
            offset=offset,
        )
