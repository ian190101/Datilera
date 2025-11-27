# app/kernel/domain/finanzas/arqueo_entidad.py
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, computed_field

class ArqueoCaja(BaseModel):
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
    
    # 'ge=0' (greater or equal) reemplaza el if < 0 del __post_init__
    # decimal_places=2 asegura precisión monetaria si se valida desde JSON
    total_ingresos: Decimal = Field(..., ge=0, decimal_places=2) 
    total_egresos: Decimal = Field(..., ge=0, decimal_places=2)
    
    # default_factory asigna la fecha UTC al momento de crear la instancia
    generado_en: datetime = Field(default_factory=datetime.utcnow)
    recalculado_en: Optional[datetime] = None
    observaciones: Optional[str] = None

    @computed_field
    def saldo(self) -> Decimal:
        """Calcula el saldo (ingresos - egresos) y lo incluye al serializar"""
        return self.total_ingresos - self.total_egresos