# app/infrastructure/db/repositories/dashboard_repo.py
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import select, func, extract, desc, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# --- TUS MODELOS REALES ---
from app.infrastructure.db.models.alumnos.alumnos import Alumno
from app.infrastructure.db.models.finanzas.pagos import Pago
# Nuevos imports basados en tus archivos:
from app.infrastructure.db.models.finanzas.plan_pago_personalizado import PlanPagoPersonalizado
from app.infrastructure.db.models.finanzas.cuota_plan_pago import CuotaPlanPago

class DashboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_metricas_generales(self, sede_id: int) -> Dict[str, Any]:
        """Calcula los KPIs usando Alumnos, Pagos y CuotaPlanPago."""
        now = datetime.now()
        inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # 1. Total Inscritos (Activos)
        q_total = select(func.count(Alumno.id)).where(
            Alumno.sede_id == sede_id,
            Alumno.estado != 'baja'
        )
        total_inscritos = await self.session.scalar(q_total) or 0

        # 2. Nuevos este Mes
        q_nuevos = select(func.count(Alumno.id)).where(
            Alumno.sede_id == sede_id,
            Alumno.creado_en >= inicio_mes
        )
        nuevos_mes = await self.session.scalar(q_nuevos) or 0

        # 3. Ingresos del Mes (Lo cobrado realmente)
        # JOIN Alumno -> Pago para filtrar por sede
        q_ingresos = (
            select(func.coalesce(func.sum(Pago.monto_pagado), 0))
            .join(Alumno, Pago.alumno_id == Alumno.id)
            .where(
                Alumno.sede_id == sede_id,
                Pago.anulado == False,
                Pago.fecha_pago >= inicio_mes.date()
            )
        )
        ingresos_mes = await self.session.scalar(q_ingresos)

        # 4. PAGOS PENDIENTES (Usando CuotaPlanPago)
        # Sumamos el saldo pendiente (monto_cuota - monto_pagado) de cuotas 'pendiente' o 'vencida'
        # Hacemos JOIN: Cuota -> Plan -> Alumno (para filtrar por sede)
        q_pendientes = (
            select(
                func.count(CuotaPlanPago.id),
                func.coalesce(func.sum(CuotaPlanPago.monto_cuota - CuotaPlanPago.monto_pagado), 0)
            )
            .join(PlanPagoPersonalizado, CuotaPlanPago.plan_id == PlanPagoPersonalizado.id)
            .join(Alumno, PlanPagoPersonalizado.alumno_id == Alumno.id)
            .where(
                Alumno.sede_id == sede_id,
                CuotaPlanPago.estado.in_(['pendiente', 'vencida'])
            )
        )
        
        try:
            res_pend = await self.session.execute(q_pendientes)
            cant_pendientes, monto_pendientes = res_pend.one()
        except Exception as e:
            print(f"Error calculando pendientes: {e}")
            cant_pendientes = 0
            monto_pendientes = 0.0

        return {
            "total_inscritos": total_inscritos,
            "inscritos_cambio_porcentaje": 0,
            "ingresos_mes": float(ingresos_mes or 0.0),
            "ingresos_objetivo_porcentaje": 0,
            "pagos_pendientes_cantidad": cant_pendientes or 0,
            "pagos_pendientes_monto": float(monto_pendientes or 0.0),
            "nuevos_mes": nuevos_mes
        }

    async def get_grafico_inscripciones(self, sede_id: int) -> Dict[str, list]:
        """Gráfico de línea: Alumnos nuevos por mes."""
        now = datetime.now()
        labels = []
        valores = []
        nombres_meses = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

        for i in range(5, -1, -1):
            fecha_ref = now - timedelta(days=30 * i)
            mes = fecha_ref.month
            anio = fecha_ref.year
            labels.append(nombres_meses[mes])
            
            query = select(func.count(Alumno.id)).where(
                Alumno.sede_id == sede_id,
                extract('month', Alumno.creado_en) == mes,
                extract('year', Alumno.creado_en) == anio
            )
            count = await self.session.scalar(query)
            valores.append(count or 0)

        return {"labels": labels, "valores": valores}

    async def get_grafico_ingresos_semanal(self, sede_id: int) -> Dict[str, list]:
        """Gráfico de barras: Ingresos reales por semana."""
        labels = []
        valores = []
        now = datetime.now()

        for i in range(3, -1, -1):
            fin = now - timedelta(weeks=i)
            inicio = fin - timedelta(days=6)
            labels.append(f"Sem {4-i}")

            q = (
                select(func.coalesce(func.sum(Pago.monto_pagado), 0))
                .join(Alumno, Pago.alumno_id == Alumno.id)
                .where(
                    Alumno.sede_id == sede_id,
                    Pago.anulado == False,
                    Pago.fecha_pago >= inicio.date(),
                    Pago.fecha_pago <= fin.date()
                )
            )
            total = await self.session.scalar(q)
            valores.append(float(total or 0.0))

        return {"labels": labels, "valores": valores}

    async def get_codigos_recientes(self, sede_id: int, limit: int = 5) -> Dict[str, list]:
        """Últimos alumnos registrados."""
        stmt = (
            select(Alumno)
            .where(Alumno.sede_id == sede_id)
            .order_by(desc(Alumno.creado_en))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        alumnos = result.scalars().all()
        
        items = []
        for alu in alumnos:
            fecha_str = alu.creado_en.strftime("%Y-%m-%d") if alu.creado_en else "---"
            items.append({
                "id": alu.id,
                "nombre_alumno": f"{alu.nombre} {alu.apellido_paterno}",
                "fecha_inscripcion": fecha_str,
                "grupo": "General", 
                "codigo_tutor": alu.codigo_unico or "---", 
                "telefono_tutor": alu.ci_numero or "---",
                "estado": alu.estado or "Registrado"
            })
        return {"items": items}