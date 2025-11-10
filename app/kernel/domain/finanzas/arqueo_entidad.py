# app/kernel/domain/finanzas/arqueo_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


@dataclass
class ArqueoCaja:
    """
    Arqueo mensual / por gestión (consolidación de Libro de Caja).

    Historias:
    - Generado automáticamente el día 6, considerando pagos hasta el 5.
    - Permite recalcular si aparecen rezagados (servicio/aplicación).
    """
    id: int
    sede_id: int
    periodo_inicio: date
    periodo_fin: date
    total_ingresos: Decimal
    total_egresos: Decimal
    generado_en: datetime = None
    recalculado_en: Optional[datetime] = None
    observaciones: Optional[str] = None

    def __post_init__(self):
        if self.total_ingresos < 0 or self.total_egresos < 0:
            raise ValueError("Totales del arqueo no pueden ser negativos.")
        self.generado_en = self.generado_en or datetime.utcnow()

    @property
    def saldo(self) -> Decimal:
        return self.total_ingresos - self.total_egresos