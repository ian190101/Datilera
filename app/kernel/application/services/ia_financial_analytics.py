from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.finanzas.categorias_egreso import CategoriaEgreso
from app.infrastructure.db.models.finanzas.categorias_pago import CategoriaPago
from app.infrastructure.db.models.finanzas.cuota_plan_pago import CuotaPlanPago
from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum
from app.infrastructure.db.models.finanzas.plan_pago_personalizado import PlanPagoPersonalizado


@dataclass(frozen=True, slots=True)
class PeriodoFinanciero:
    inicio: date
    fin: date
    etiqueta: str


class AnaliticaFinancieraIA:
    """Consultas financieras de solo lectura para el copiloto.

    Centralizar estas consultas evita que el modelo generativo invente cifras y
    garantiza que cada resultado quede limitado a la sede de la sesión.
    """

    COLORES = {
        "ingreso": "#10b981",
        "egreso": "#f97316",
        "saldo": "#6366f1",
        "pendiente": "#ef4444",
        "mora": "#dc2626",
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def obtener(self, sede_id: int, periodo: PeriodoFinanciero) -> dict[str, Any]:
        resumen = await self._resumen_caja(sede_id, periodo)
        tendencia = await self._tendencia(sede_id, periodo)
        categorias_ingreso = await self._categorias(sede_id, periodo, TipoMovimientoEnum.INGRESO)
        categorias_egreso = await self._categorias(sede_id, periodo, TipoMovimientoEnum.EGRESO)
        cartera = await self._cartera_pendiente(sede_id, periodo.fin)
        return {
            **resumen,
            "periodo": periodo,
            "tendencia": tendencia,
            "categorias_ingreso": categorias_ingreso,
            "categorias_egreso": categorias_egreso,
            "cartera": cartera,
        }

    async def _resumen_caja(self, sede_id: int, periodo: PeriodoFinanciero) -> dict[str, Any]:
        stmt = select(
            func.coalesce(
                func.sum(case((LibroCaja.tipo == TipoMovimientoEnum.INGRESO, LibroCaja.monto), else_=0)), 0
            ),
            func.coalesce(
                func.sum(case((LibroCaja.tipo == TipoMovimientoEnum.EGRESO, LibroCaja.monto), else_=0)), 0
            ),
            func.count(LibroCaja.id),
        ).where(
            LibroCaja.sede_id == sede_id,
            LibroCaja.fecha >= periodo.inicio,
            LibroCaja.fecha <= periodo.fin,
        )
        ingresos, egresos, movimientos = (await self.db.execute(stmt)).one()
        ingresos_d = Decimal(ingresos or 0)
        egresos_d = Decimal(egresos or 0)
        return {
            "ingresos": float(ingresos_d),
            "egresos": float(egresos_d),
            "saldo": float(ingresos_d - egresos_d),
            "movimientos": int(movimientos or 0),
        }

    async def _tendencia(self, sede_id: int, periodo: PeriodoFinanciero) -> list[dict[str, Any]]:
        stmt = (
            select(LibroCaja.fecha, LibroCaja.tipo, func.sum(LibroCaja.monto))
            .where(
                LibroCaja.sede_id == sede_id,
                LibroCaja.fecha >= periodo.inicio,
                LibroCaja.fecha <= periodo.fin,
            )
            .group_by(LibroCaja.fecha, LibroCaja.tipo)
            .order_by(LibroCaja.fecha)
        )
        rows = (await self.db.execute(stmt)).all()
        por_mes = (periodo.fin - periodo.inicio).days > 62
        agrupado: dict[str, dict[str, float]] = defaultdict(lambda: {"ingresos": 0.0, "egresos": 0.0})
        for fecha, tipo, monto in rows:
            clave = fecha.strftime("%Y-%m") if por_mes else fecha.isoformat()
            campo = "ingresos" if tipo == TipoMovimientoEnum.INGRESO else "egresos"
            agrupado[clave][campo] += float(monto or 0)
        return [
            {"periodo": clave, **valores, "saldo": valores["ingresos"] - valores["egresos"]}
            for clave, valores in sorted(agrupado.items())
        ]

    async def _categorias(
        self,
        sede_id: int,
        periodo: PeriodoFinanciero,
        tipo: TipoMovimientoEnum,
    ) -> list[dict[str, Any]]:
        if tipo == TipoMovimientoEnum.INGRESO:
            nombre = CategoriaPago.nombre
            stmt = select(nombre, func.sum(LibroCaja.monto)).outerjoin(
                CategoriaPago, LibroCaja.categoria_pago_id == CategoriaPago.id
            )
        else:
            nombre = CategoriaEgreso.nombre
            stmt = select(nombre, func.sum(LibroCaja.monto)).outerjoin(
                CategoriaEgreso, LibroCaja.categoria_egreso_id == CategoriaEgreso.id
            )
        stmt = (
            stmt.where(
                LibroCaja.sede_id == sede_id,
                LibroCaja.tipo == tipo,
                LibroCaja.fecha >= periodo.inicio,
                LibroCaja.fecha <= periodo.fin,
            )
            .group_by(nombre)
            .order_by(func.sum(LibroCaja.monto).desc())
        )
        rows = (await self.db.execute(stmt)).all()
        return [{"categoria": categoria or "Sin categoría", "monto": float(monto or 0)} for categoria, monto in rows]

    async def _cartera_pendiente(self, sede_id: int, al_dia: date) -> dict[str, Any]:
        saldo_cuota = (
            func.coalesce(CuotaPlanPago.monto_cuota, 0)
            - func.coalesce(CuotaPlanPago.monto_pagado, 0)
            + func.coalesce(CuotaPlanPago.mora, 0)
        )
        estado_pendiente = CuotaPlanPago.estado.in_(("pendiente", "vencida"))
        stmt = (
            select(
                func.coalesce(func.sum(case((estado_pendiente, saldo_cuota), else_=0)), 0),
                func.count(case((estado_pendiente, CuotaPlanPago.id))),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                estado_pendiente & (CuotaPlanPago.fecha_vencimiento < al_dia),
                                saldo_cuota,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ),
                func.count(
                    case(
                        (
                            estado_pendiente & (CuotaPlanPago.fecha_vencimiento < al_dia),
                            CuotaPlanPago.id,
                        )
                    )
                ),
            )
            .join(PlanPagoPersonalizado, CuotaPlanPago.plan_id == PlanPagoPersonalizado.id)
            .where(
                PlanPagoPersonalizado.sede_id == sede_id,
                PlanPagoPersonalizado.estado == "activo",
            )
        )
        pendiente, cuotas_pendientes, vencido, cuotas_vencidas = (await self.db.execute(stmt)).one()
        return {
            "pendiente": float(pendiente or 0),
            "cuotas_pendientes": int(cuotas_pendientes or 0),
            "vencido": float(vencido or 0),
            "cuotas_vencidas": int(cuotas_vencidas or 0),
        }

    @classmethod
    def construir_graficos(cls, datos: dict[str, Any], enfoque: str = "resumen") -> list[dict[str, Any]]:
        graficos: list[dict[str, Any]] = []
        tendencia = datos["tendencia"]
        if tendencia:
            graficos.append({
                "type": "line",
                "title": "Evolución del flujo de caja",
                "labels": [item["periodo"] for item in tendencia],
                "datasets": [
                    {
                        "label": "Ingresos",
                        "data": [item["ingresos"] for item in tendencia],
                        "borderColor": cls.COLORES["ingreso"],
                        "backgroundColor": "rgba(16, 185, 129, 0.15)",
                        "fill": False,
                    },
                    {
                        "label": "Egresos",
                        "data": [item["egresos"] for item in tendencia],
                        "borderColor": cls.COLORES["egreso"],
                        "backgroundColor": "rgba(249, 115, 22, 0.15)",
                        "fill": False,
                    },
                ],
            })

        categorias = datos["categorias_egreso"] if enfoque == "egresos" else datos["categorias_ingreso"]
        if categorias:
            principales = categorias[:7]
            resto = sum(item["monto"] for item in categorias[7:])
            if resto:
                principales.append({"categoria": "Otros", "monto": resto})
            graficos.append({
                "type": "doughnut",
                "title": "Distribución por categoría",
                "labels": [item["categoria"] for item in principales],
                "datasets": [{
                    "label": "Monto (Bs)",
                    "data": [item["monto"] for item in principales],
                    "backgroundColor": [
                        "#6366f1", "#10b981", "#f59e0b", "#ef4444",
                        "#06b6d4", "#8b5cf6", "#84cc16", "#64748b",
                    ][:len(principales)],
                }],
            })
        elif not graficos:
            graficos.append({
                "type": "bar",
                "title": "Resumen del período",
                "labels": ["Ingresos", "Egresos", "Resultado neto"],
                "datasets": [{
                    "label": "Monto (Bs)",
                    "data": [datos["ingresos"], datos["egresos"], datos["saldo"]],
                    "backgroundColor": [cls.COLORES["ingreso"], cls.COLORES["egreso"], cls.COLORES["saldo"]],
                }],
            })
        return graficos[:2]
