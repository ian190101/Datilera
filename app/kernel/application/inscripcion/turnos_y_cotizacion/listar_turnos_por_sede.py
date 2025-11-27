# app/application/inscripcion/turnos_y_cotizacion/listar_turnos_por_sede.py
from dataclasses import dataclass
from typing import List, Protocol, Optional

# Protocols mínimos para adaptadores existentes
class TurnosRepositoryPort(Protocol):
    async def listar_por_sede(self, sede_id: int) -> List[dict]: ...

class PreciosTurnosRepositoryPort(Protocol):
    async def obtener_precio(self, turno_id: int, categoria_pago_id: Optional[int], gestion: int) -> Optional[dict]: ...

@dataclass
class ListarTurnosPorSedeQuery:
    sede_id: int
    gestion: int
    categoria_pago_id: Optional[int] = None  # si aplica

class ListarTurnosPorSedeUseCase:
    def __init__(self, turnos_repo: TurnosRepositoryPort, precios_repo: PreciosTurnosRepositoryPort):
        self.turnos_repo = turnos_repo
        self.precios_repo = precios_repo

    async def execute(self, q: ListarTurnosPorSedeQuery) -> List[dict]:
        turnos = await self.turnos_repo.listar_por_sede(q.sede_id)
        result: List[dict] = []
        for t in turnos:
            precio = await self.precios_repo.obtener_precio(t["id"], q.categoria_pago_id, q.gestion)
            result.append({**t, "precio_vigente": precio["monto"] if precio else None})
        return result
