from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract, case, literal
from datetime import date
from decimal import Decimal

# Modelos
from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum
from app.infrastructure.db.models.finanzas.cuota_plan_pago import CuotaPlanPago
from app.infrastructure.db.models.finanzas.plan_pago_personalizado import PlanPagoPersonalizado # <--- IMPORTANTE: Agregado
from app.infrastructure.db.models.finanzas.pagos import Pago
from app.infrastructure.db.models.finanzas.egresos import Egreso
from app.infrastructure.db.models.finanzas.categorias_pago import CategoriaPago
from app.infrastructure.db.models.finanzas.categorias_egreso import CategoriaEgreso

class ArqueoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generar_reporte_eeff(self, sede_id: int, mes: int | None, anio: int) -> dict:
        """
        Genera el reporte idéntico al 'EEFF.csv'.
        Si mes es None, genera el reporte anual (Cierre de Gestión).
        """
        
        # --- 1. INGRESOS: POR COBRAR (Lo que debió entrar) ---
        # CORRECCIÓN: Usamos paréntesis para evitar errores de indentación
        stmt_por_cobrar = (
            select(
                CategoriaPago.nombre,
                func.sum(CuotaPlanPago.monto_cuota)
            )
            .join(CuotaPlanPago.plan) # Unimos con el Plan
            .where(PlanPagoPersonalizado.sede_id == sede_id) # Filtramos Sede correctamente
            .outerjoin(CategoriaPago, CategoriaPago.id == 1) # Simplificación
            .where(
                and_(
                    # Si hay mes, filtramos por mes. Si es None, traemos todo el año.
                    extract('month', CuotaPlanPago.fecha_vencimiento) == mes if mes else True,
                    extract('year', CuotaPlanPago.fecha_vencimiento) == anio
                )
            )
            .group_by(CategoriaPago.nombre)
        )
        
        # --- 2. INGRESOS: RECAUDADO REAL (Lo que entró a Caja) ---
        stmt_ingresos_reales = (
            select(
                CategoriaPago.nombre,
                func.sum(LibroCaja.monto)
            )
            .join(CategoriaPago, LibroCaja.categoria_pago_id == CategoriaPago.id)
            .where(
                and_(
                    LibroCaja.sede_id == sede_id,
                    LibroCaja.tipo == TipoMovimientoEnum.INGRESO,
                    extract('month', LibroCaja.fecha) == mes if mes else True,
                    extract('year', LibroCaja.fecha) == anio
                )
            )
            .group_by(CategoriaPago.nombre)
        )
        
        ingresos_reales = (await self.db.execute(stmt_ingresos_reales)).all()
        dict_ingresos = {row[0]: float(row[1]) for row in ingresos_reales}

        # --- 3. EGRESOS (Gastos Fijos, Sueldos, Variables) ---
        stmt_egresos = (
            select(
                CategoriaEgreso.nombre,
                func.sum(LibroCaja.monto)
            )
            .join(CategoriaEgreso, LibroCaja.categoria_egreso_id == CategoriaEgreso.id)
            .where(
                and_(
                    LibroCaja.sede_id == sede_id,
                    LibroCaja.tipo == TipoMovimientoEnum.EGRESO,
                    extract('month', LibroCaja.fecha) == mes if mes else True,
                    extract('year', LibroCaja.fecha) == anio
                )
            )
            .group_by(CategoriaEgreso.nombre)
        )
         
        egresos_reales = (await self.db.execute(stmt_egresos)).all()
        dict_egresos = {row[0]: float(row[1]) for row in egresos_reales}

        # --- 4. DESGLOSE POR CUENTA (Efectivo vs Bancos) ---
        stmt_bancos_ingreso = (
            select(
                Pago.metodo_pago,
                func.sum(Pago.monto_pagado)
            )
            .join(LibroCaja, LibroCaja.pago_id == Pago.id)
            .where(
                and_(
                    LibroCaja.sede_id == sede_id,
                    extract('month', LibroCaja.fecha) == mes if mes else True,
                    extract('year', LibroCaja.fecha) == anio
                )
            )
            .group_by(Pago.metodo_pago)
        )
         
        bancos_ingreso = (await self.db.execute(stmt_bancos_ingreso)).all()
        
        stmt_bancos_egreso = (
            select(
                Egreso.metodo_pago,
                func.sum(Egreso.monto)
            )
            .join(LibroCaja, LibroCaja.egreso_id == Egreso.id)
            .where(
                and_(
                    LibroCaja.sede_id == sede_id,
                    extract('month', LibroCaja.fecha) == mes if mes else True,
                    extract('year', LibroCaja.fecha) == anio
                )
            )
            .group_by(Egreso.metodo_pago)
        )
         
        bancos_egreso = (await self.db.execute(stmt_bancos_egreso)).all()

        # Consolidar Saldos
        cuentas = {}
        for metodo, monto in bancos_ingreso:
            cuentas[metodo] = cuentas.get(metodo, 0) + float(monto)
        for metodo, monto in bancos_egreso:
            cuentas[metodo] = cuentas.get(metodo, 0) - float(monto)

        # --- 5. ARMADO DEL REPORTE FINAL ---
        total_ingresos = sum(dict_ingresos.values())
        total_gastos = sum(dict_egresos.values())
        
        reporte = {
            "periodo": f"{mes if mes else 'ANUAL'}/{anio}",
            "resumen_ingresos": [
                {
                    "item": cat, 
                    "por_cobrar": 0, 
                    "recaudado": monto, 
                    "saldo_pendiente": 0
                } for cat, monto in dict_ingresos.items()
            ],
            "resumen_gastos": [
                {"item": cat, "monto": monto} for cat, monto in dict_egresos.items()
            ],
            "totales": {
                "total_ingresos_reales": total_ingresos,
                "total_gastos": total_gastos,
                "utilidad_operativa": total_ingresos - total_gastos
            },
            "disponibilidad_cuentas": cuentas
        }
        
        return reporte

    async def cierre_gestion(self, sede_id: int, anio: int) -> dict:
        return await self.generar_reporte_eeff(sede_id, None, anio)