## app/kernel/domain/finanzas/turno_precio.py
from __future__ import annotations
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict, model_validator

class PrecioTurnoVigencia(BaseModel):
    """
    VO de precio con **vigencia** por sede y **turno_id**.

    Historias:
    - Precios por sede; solo superadmin/directora modifican.
    - Mantener historial de cambios (aplica a nuevos inscritos).
    """
    # frozen=True hace que la instancia sea inmutable (hashable), igual que el dataclass frozen
    model_config = ConfigDict(frozen=True)

    sede_id: int
    turno_id: int
    
    # Validación: monto debe ser positivo. decimal_places=2 ayuda en la serialización.
    monto: Decimal = Field(..., gt=0, decimal_places=2)
    vigente_desde: date


class TurnoPrecio(BaseModel):
    """
    Agregado de **vigencias de precio** de un turno (turno_id) por sede.

    Métodos clave:
    - `precio_vigente(fecha)` obtiene el precio aplicable en una fecha.
    - `prorratear_primer_pago(...)` regla 20 días; si faltan <=3 días
      para terminar el mes, se cobra desde el 1° del mes siguiente.
    - Redondeo boliviano a **0,50 Bs**.
    - Descuentos (solo mensualidad Cochabamba): 3% medio año, 6% anual.
    """
    sede_id: int
    turno_id: int
    vigencias: List[PrecioTurnoVigencia]

    @model_validator(mode='after')
    def validar_y_ordenar_vigencias(self) -> TurnoPrecio:
        """
        Valida que existan vigencias y las ordena cronológicamente
        para facilitar la búsqueda del precio vigente.
        """
        if not self.vigencias:
            raise ValueError("Debe existir al menos una vigencia de precio.")
        
        # Ordenamos la lista in-place por fecha
        self.vigencias.sort(key=lambda v: v.vigente_desde)
        return self

    # --- Consulta de precio vigente ---

    def precio_vigente(self, en_fecha: date) -> Decimal:
        """Busca el precio activo para la fecha dada recorriendo el historial ordenado."""
        actual = None
        for v in self.vigencias:
            if v.vigente_desde <= en_fecha:
                actual = v.monto
            else:
                # Como están ordenadas, si pasamos la fecha, ya no hay vigencias futuras aplicables
                break
        
        if actual is None:
            raise ValueError("No hay precio vigente para la fecha indicada.")
        
        return actual

    # --- Reglas de negocio (Helpers Estáticos) ---

    @staticmethod
    def _redondear_media_unidad(monto: Decimal) -> Decimal:
        """
        Regla de redondeo boliviano:
        - Fracción <= 0.49  -> 0.50
        - Fracción >= 0.51  -> +1.00
        - Fracción == 0.50  -> 0.50
        """
        # Aseguramos dos decimales base
        monto = monto.quantize(Decimal("0.01"))
        entero = int(monto)
        # Extraemos la fracción
        fr = (monto - Decimal(entero)).quantize(Decimal("0.01"))

        if fr == Decimal("0.00"):
            return Decimal(entero)
        if fr <= Decimal("0.49"):
            return Decimal(entero) + Decimal("0.50")
        if fr >= Decimal("0.51"):
            return Decimal(entero + 1)
        # Caso exacto 0.50
        return Decimal(entero) + Decimal("0.50")

    @staticmethod
    def _primer_dia_mes_siguiente(fecha: date) -> date:
        year = fecha.year + (1 if fecha.month == 12 else 0)
        month = 1 if fecha.month == 12 else fecha.month + 1
        return date(year, month, 1)

    @staticmethod
    def _dias_restantes_mes(fecha: date) -> int:
        """Días calendario restantes (incluyendo `fecha`)."""
        # Se llama a la clase explícitamente para métodos estáticos dentro de la misma clase
        fin_mes = TurnoPrecio._primer_dia_mes_siguiente(fecha) - timedelta(days=1)
        return (fin_mes - fecha).days + 1

    # --- Lógica Principal ---

    def prorratear_primer_pago(
        self,
        fecha_primera_asistencia: date,
        dias_a_cobrar: Optional[int] = None,
        aplicar_descuento: Optional[str] = None,  # "medio_anio" | "anio" | None
    ) -> Tuple[Decimal, date]:
        """
        Calcula el primer pago retornando (monto_a_pagar, fecha_inicio_periodo).
        Aplica reglas de fin de mes, prorrateo proporcional y descuentos semestrales/anuales.
        """
        precio = self.precio_vigente(fecha_primera_asistencia)
        
        # Regla: si <= 3 días para fin de mes, cobrar desde el siguiente mes (monto mensual completo)
        if self._dias_restantes_mes(fecha_primera_asistencia) <= 3:
            monto = precio
            inicio_periodo = self._primer_dia_mes_siguiente(fecha_primera_asistencia)
        else:
            # Estimar días a cobrar si no se provee: proporcional a calendario (base 20 días)
            if dias_a_cobrar is None:
                fin_mes = self._primer_dia_mes_siguiente(fecha_primera_asistencia) - timedelta(days=1)
                dias_mes = fin_mes.day
                propor = Decimal(self._dias_restantes_mes(fecha_primera_asistencia)) / Decimal(dias_mes)
                # Cálculo de días estimados
                dias_calculados = int((propor * Decimal(20)).quantize(Decimal("1.")))
                dias_a_cobrar = max(1, min(20, dias_calculados))

            # Precio por día (base 20 días laborales aprox)
            monto_dia = (precio / Decimal(20)).quantize(Decimal("0.01"))
            monto = monto_dia * Decimal(dias_a_cobrar)
            inicio_periodo = fecha_primera_asistencia

        # Aplicar descuentos por pago adelantado (solo mensualidad)
        if aplicar_descuento == "medio_anio":
            monto = (monto * Decimal("0.97")).quantize(Decimal("0.01"))
        elif aplicar_descuento == "anio":
            monto = (monto * Decimal("0.94")).quantize(Decimal("0.01"))

        return self._redondear_media_unidad(monto), inicio_periodo