# app/kernel/application/calendario/eventos/listar_eventos_por_mes.py

from datetime import date
from typing import List, Optional
from calendar import monthrange

from app.kernel.domain.calendario import (
    EventoCalendario,
    EventoCalendarioRepositoryPort,
)


class ListarEventosPorMesUseCase:
    """Caso de uso: Listar eventos de un mes específico."""
    
    def __init__(self, evento_repo: EventoCalendarioRepositoryPort):
        self.evento_repo = evento_repo
    
    async def ejecutar(
        self,
        anio: int,
        mes: int,
        sede_id: Optional[int] = None,
        solo_aprobados: bool = True,
    ) -> List[EventoCalendario]:
        """Lista eventos de un mes específico.
        
        Args:
            anio: Año
            mes: Mes (1-12)
            sede_id: Filtrar por sede (opcional)
            solo_aprobados: Solo eventos aprobados
            
        Returns:
            Lista de EventoCalendario del mes
        """
        # Calcular primer y último día del mes
        primer_dia = date(anio, mes, 1)
        ultimo_dia_numero = monthrange(anio, mes)[1]
        ultimo_dia = date(anio, mes, ultimo_dia_numero)
        
        return await self.evento_repo.listar(
            sede_id=sede_id,
            fecha_inicio=primer_dia,
            fecha_fin=ultimo_dia,
            aprobado=True if solo_aprobados else None,
        )
