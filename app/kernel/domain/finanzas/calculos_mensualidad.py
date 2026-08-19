"""Reglas puras para calcular el primer cobro de una mensualidad."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

DOS_DECIMALES = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class ResultadoProrrateo:
    """Resultado inmutable del cálculo del primer mes."""

    fecha_inicio_cobro: date
    dias_habiles_cobrados: int
    monto: Decimal
    diferido: bool


def redondear_a_medio_boliviano(monto: Decimal) -> Decimal:
    """Redondea a importes terminados en 0,00 o 0,50 sin alterar enteros exactos."""

    monto = monto.quantize(DOS_DECIMALES)
    parte_entera = monto // Decimal("1")
    centavos = monto - parte_entera
    if centavos == Decimal("0.00"):
        return monto
    if centavos <= Decimal("0.50"):
        return (parte_entera + Decimal("0.50")).quantize(DOS_DECIMALES)
    return (parte_entera + Decimal("1.00")).quantize(DOS_DECIMALES)


def primer_dia_mes_siguiente(fecha: date) -> date:
    """Obtiene el primer día del mes siguiente, incluyendo el cambio de año."""

    if fecha.month == 12:
        return date(fecha.year + 1, 1, 1)
    return date(fecha.year, fecha.month + 1, 1)


def calcular_prorrateo_mensualidad(
    fecha_ingreso: date,
    monto_mensual: Decimal,
) -> ResultadoProrrateo:
    """Aplica la regla institucional de 20 días hábiles y cierre de tres días."""

    if monto_mensual <= 0:
        raise ValueError("La mensualidad debe ser mayor que cero")

    ultimo_dia = calendar.monthrange(fecha_ingreso.year, fecha_ingreso.month)[1]
    dias_calendario_restantes = ultimo_dia - fecha_ingreso.day
    if dias_calendario_restantes <= 3:
        return ResultadoProrrateo(
            fecha_inicio_cobro=primer_dia_mes_siguiente(fecha_ingreso),
            dias_habiles_cobrados=0,
            monto=monto_mensual.quantize(DOS_DECIMALES),
            diferido=True,
        )

    dias_habiles = 0
    cursor = fecha_ingreso
    while cursor.month == fecha_ingreso.month:
        if cursor.weekday() < 5:
            dias_habiles += 1
        cursor += timedelta(days=1)

    dias_habiles = min(dias_habiles, 20)
    costo_diario = monto_mensual / Decimal("20")
    monto = redondear_a_medio_boliviano(costo_diario * Decimal(dias_habiles))
    return ResultadoProrrateo(
        fecha_inicio_cobro=fecha_ingreso,
        dias_habiles_cobrados=dias_habiles,
        monto=monto,
        diferido=False,
    )


def fecha_vencimiento_primera_cuota(fecha_inicio_cobro: date) -> date:
    """Evita que la primera cuota venza antes de que el alumno empiece."""

    dia_diez = fecha_inicio_cobro.replace(day=10)
    return max(dia_diez, fecha_inicio_cobro)
