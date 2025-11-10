from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class PrecioTurnoVigencia:
    """
    VO de precio con **vigencia** por sede y **turno_id**.

    Historias:
    - Precios por sede; solo superadmin/directora modifican.
    - Mantener historial de cambios (aplica a nuevos inscritos).
    """
    sede_id: int
    turno_id: int
    monto: Decimal
    vigente_desde: date

    def __post_init__(self):
        if Decimal(self.monto) <= 0:
            raise ValueError("El monto del turno debe ser > 0.")


class TurnoPrecio:
    """
    Agregado de **vigencias de precio** de un turno (turno_id) por sede.

    Métodos clave:
    - `precio_vigente(fecha)` obtiene el precio aplicable en una fecha.
    - `prorratear_primer_pago(...)` regla 20 días; si faltan ≤3 días
      para terminar el mes, se cobra desde el 1° del mes siguiente.
    - Redondeo boliviano a **0,50 Bs**.
    - Descuentos (solo mensualidad Cochabamba): 3% medio año, 6% anual.
    """

    def __init__(self, sede_id: int, turno_id: int, vigencias: List[PrecioTurnoVigencia]):
        if not vigencias:
            raise ValueError("Debe existir al menos una vigencia de precio.")
        self.sede_id = sede_id
        self.turno_id = turno_id
        # ordenamos por fecha de vigencia
        self.vigencias = sorted(vigencias, key=lambda v: v.vigente_desde)

    # --- Consulta de precio vigente ---
    def precio_vigente(self, en_fecha: date) -> Decimal:
        actual = None
        for v in self.vigencias:
            if v.vigente_desde <= en_fecha:
                actual = v.monto
            else:
                break
        if actual is None:
            raise ValueError("No hay precio vigente para la fecha indicada.")
        return Decimal(actual)

    # --- Reglas de negocio ---

    @staticmethod
    def _redondear_media_unidad(monto: Decimal) -> Decimal:
        """
        Regla de redondeo boliviano:
        - Fracción <= 0.49  -> 0.50
        - Fracción >= 0.51  -> +1.00
        - Fracción == 0.50  -> 0.50
        Se permiten múltiplos de 0.50 Bs.
        """
        monto = Decimal(monto).quantize(Decimal("0.01"))
        entero = int(monto)
        fr = (monto - Decimal(entero)).quantize(Decimal("0.01"))
        if fr == Decimal("0.00"):
            return Decimal(entero)
        if fr <= Decimal("0.49"):
            return Decimal(entero) + Decimal("0.50")
        if fr >= Decimal("0.51"):
            return Decimal(entero + 1)
        return Decimal(entero) + Decimal("0.50")

    @staticmethod
    def _primer_dia_mes_siguiente(fecha: date) -> date:
        year = fecha.year + (1 if fecha.month == 12 else 0)
        month = 1 if fecha.month == 12 else fecha.month + 1
        return date(year, month, 1)

    @staticmethod
    def _dias_restantes_mes(fecha: date) -> int:
        """Días calendario restantes (incluyendo `fecha`)."""
        fin_mes = TurnoPrecio._primer_dia_mes_siguiente(fecha) - timedelta(days=1)
        return (fin_mes - fecha).days + 1

    def prorratear_primer_pago(
        self,
        fecha_primera_asistencia: date,
        dias_a_cobrar: Optional[int] = None,
        aplicar_descuento: Optional[str] = None,  # "medio_anio" | "anio" | None
    ) -> tuple[Decimal, date]:
        """
        Calcula el primer pago:
        - Si faltan ≤3 días para que acabe el mes => se cobra desde el 1° del mes siguiente (monto = mensualidad completa).
        - Si no, prorratea a razón de (precio/20) * días_a_cobrar.
          Si `dias_a_cobrar` es None, se estima proporcional a calendario (20 * días_restantes / días_del_mes).
        - Descuento aplica solo a mensualidades (Cochabamba) cuando `aplicar_descuento` sea "medio_anio" (3%) o "anio" (6%).
        Retorna (monto_primer_pago, fecha_inicio_periodo_cobrado).
        """
        precio = self.precio_vigente(fecha_primera_asistencia)
        # Regla: si <= 3 días para fin de mes, cobrar desde el siguiente mes (monto mensual)
        if self._dias_restantes_mes(fecha_primera_asistencia) <= 3:
            monto = precio
            inicio_periodo = self._primer_dia_mes_siguiente(fecha_primera_asistencia)
        else:
            # Estimar días a cobrar si no se provee: proporcional a calendario (20 como referencia fija)
            if dias_a_cobrar is None:
                fin_mes = self._primer_dia_mes_siguiente(fecha_primera_asistencia) - timedelta(days=1)
                dias_mes = fin_mes.day
                propor = Decimal(self._dias_restantes_mes(fecha_primera_asistencia)) / Decimal(dias_mes)
                dias_a_cobrar = int((propor * Decimal(20)).quantize(Decimal("1.")))  # nearest integer
                dias_a_cobrar = max(1, min(20, dias_a_cobrar))

            monto_dia = (precio / Decimal(20)).quantize(Decimal("0.01"))
            monto = monto_dia * Decimal(dias_a_cobrar)
            inicio_periodo = fecha_primera_asistencia

        # Descuento (solo mensualidad): 3% medio año, 6% año
        if aplicar_descuento == "medio_anio":
            monto = (monto * Decimal("0.97")).quantize(Decimal("0.01"))
        elif aplicar_descuento == "anio":
            monto = (monto * Decimal("0.94")).quantize(Decimal("0.01"))

        return self._redondear_media_unidad(monto), inicio_periodo