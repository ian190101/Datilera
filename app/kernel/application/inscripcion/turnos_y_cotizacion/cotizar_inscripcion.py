# app/application/inscripcion/turnos_y_cotizacion/cotizar_inscripcion.py
from typing import Optional, Protocol
from pydantic import BaseModel
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

class PreciosTurnosRepositoryPort(Protocol):
    async def obtener_precio(self, turno_id: int, categoria_pago_id: Optional[int], gestion: int) -> Optional[dict]: ...

class CotizarInscripcionCommand(BaseModel):
    sede_id: int
    turno_id: int
    gestion: int
    categoria_pago_id: Optional[int] = None
    fecha_inicio: date
    aplica_desc_anual: bool = False
    aplica_desc_semestral: bool = False

class CotizarInscripcionUseCase:
    DIAS_BASE = Decimal("20")
    CORTE_MINIMO = 3

    def __init__(self, precios_repo: PreciosTurnosRepositoryPort):
        self.precios_repo = precios_repo

    async def execute(self, cmd: CotizarInscripcionCommand) -> dict:
        row = await self.precios_repo.obtener_precio(cmd.turno_id, cmd.categoria_pago_id, cmd.gestion)
        if not row:
            return {"monto": Decimal("0.00"), "detalle": "Sin precio vigente"}
        mensual = Decimal(str(row["monto"]))
        dias_restantes = max(0, (date(cmd.fecha_inicio.year, cmd.fecha_inicio.month, 28) - cmd.fecha_inicio).days)
        if dias_restantes <= self.CORTE_MINIMO:
            prorr = Decimal("0.00")
            detalle = f"≤{self.CORTE_MINIMO} días, difiere a próximo mes"
        else:
            factor = Decimal(dias_restantes) / self.DIAS_BASE
            prorr = (mensual * factor).quantize(Decimal("0.50"), rounding=ROUND_HALF_UP)
            detalle = f"{dias_restantes} días sobre {self.DIAS_BASE}"
        desc = Decimal("0.00")
        if cmd.aplica_desc_anual:
            desc += prorr * Decimal("0.06")
        elif cmd.aplica_desc_semestral:
            desc += prorr * Decimal("0.03")
        total = (prorr - desc).quantize(Decimal("0.50"), rounding=ROUND_HALF_UP)
        return {"monto_mensual": mensual, "prorrateado": prorr, "descuento": desc.quantize(Decimal("0.01")), "total": total, "detalle": detalle}
