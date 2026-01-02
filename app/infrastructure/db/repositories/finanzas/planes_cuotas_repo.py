# app/infrastructure/db/repositories/finanzas/planes_cuotas_repo.py
from typing import Optional, List, Dict, Tuple, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, case, func, and_, or_, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas.planes_cuotas import PlanCuota, EstadoCuota


class PlanesCuotasRepository(BaseRepository[PlanCuota]):
    """
    Repositorio para cuotas de planes de pago (tabla de amortización).
    Gestiona cuotas individuales, vencimientos y estados.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, PlanCuota)

    # ==================== HELPERS INTERNOS ====================

    def _get_column(self, name: str) -> InstrumentedAttribute[Any]:
        """
        Helper para obtener columna con tipo seguro.
        
        Args:
            name: Nombre del atributo de la columna
            
        Returns:
            Columna tipada
            
        Raises:
            AssertionError: Si la columna no existe
        """
        col = getattr(PlanCuota, name, None)
        assert col is not None, f"PlanCuota no tiene atributo '{name}'"
        return col

    # ==================== CONSULTAS BÁSICAS ====================

    async def listar_por_plan(
        self,
        plan_pago_id: int,
        estado: Optional[EstadoCuota] = None
    ) -> List[PlanCuota]:
        """
        Lista cuotas de un plan de pago.
        
        Args:
            plan_pago_id: ID del plan de pago
            estado: Filtrar por estado específico (opcional)
        """
        plan_pago_id_col = self._get_column('plan_pago_id')
        estado_col = self._get_column('estado')
        numero_cuota_col = self._get_column('numero_cuota')
        
        stmt = select(PlanCuota).where(plan_pago_id_col == plan_pago_id)
        
        if estado:
            stmt = stmt.where(estado_col == estado)
        
        stmt = stmt.order_by(numero_cuota_col.asc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obtener_cuota_numero(
        self,
        plan_pago_id: int,
        numero_cuota: int
    ) -> Optional[PlanCuota]:
        """Obtiene una cuota específica por su número."""
        plan_pago_id_col = self._get_column('plan_pago_id')
        numero_cuota_col = self._get_column('numero_cuota')
        
        stmt = select(PlanCuota).where(
            and_(
                plan_pago_id_col == plan_pago_id,
                numero_cuota_col == numero_cuota
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def obtener_proxima_cuota_pendiente(
        self,
        plan_pago_id: int
    ) -> Optional[PlanCuota]:
        """Obtiene la siguiente cuota pendiente de pago."""
        plan_pago_id_col = self._get_column('plan_pago_id')
        estado_col = self._get_column('estado')
        numero_cuota_col = self._get_column('numero_cuota')
        
        stmt = (
            select(PlanCuota)
            .where(
                and_(
                    plan_pago_id_col == plan_pago_id,
                    estado_col == EstadoCuota.pendiente
                )
            )
            .order_by(numero_cuota_col.asc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ==================== VENCIMIENTOS ====================

    async def listar_vencidas(
        self,
        hasta_fecha: Optional[date] = None,
        limit: int = 100
    ) -> List[PlanCuota]:
        """
        Lista cuotas vencidas (fecha_vencimiento pasada y estado != pagado).
        
        Args:
            hasta_fecha: Fecha límite (default: hoy)
            limit: Límite de resultados
        """
        fecha_limite: date = hasta_fecha or date.today()
        
        fecha_venc_col = self._get_column('fecha_vencimiento')
        estado_col = self._get_column('estado')
        
        stmt = (
            select(PlanCuota)
            .where(
                and_(
                    fecha_venc_col < fecha_limite,
                    or_(
                        estado_col == EstadoCuota.pendiente,
                        estado_col == EstadoCuota.vencido
                    )
                )
            )
            .order_by(fecha_venc_col.asc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def marcar_vencidas(self) -> int:
        """
        Marca como 'vencido' todas las cuotas pendientes con fecha pasada.
        
        Returns:
            Cantidad de cuotas marcadas como vencidas
        """
        fecha_venc_col = self._get_column('fecha_vencimiento')
        estado_col = self._get_column('estado')
        
        stmt = (
            select(PlanCuota)
            .where(
                and_(
                    fecha_venc_col < date.today(),
                    estado_col == EstadoCuota.pendiente
                )
            )
        )
        
        result = await self.session.execute(stmt)
        cuotas_vencidas: List[PlanCuota] = list(result.scalars().all())
        
        for cuota in cuotas_vencidas:
            # ✅ Actualizar con setattr
            assert hasattr(cuota, 'estado'), "PlanCuota debe tener 'estado'"
            setattr(cuota, 'estado', EstadoCuota.vencido)
            
            assert hasattr(cuota, 'actualizado_en'), "PlanCuota debe tener 'actualizado_en'"
            setattr(cuota, 'actualizado_en', datetime.utcnow())
        
        await self.session.flush()
        
        return len(cuotas_vencidas)

    async def listar_proximas_vencer(
        self,
        dias_anticipacion: int = 5,
        limit: int = 50
    ) -> List[PlanCuota]:
        """
        Lista cuotas que vencen en los próximos X días.
        
        Args:
            dias_anticipacion: Días de anticipación
            limit: Límite de resultados
        """
        fecha_inicio: date = date.today()
        fecha_limite: date = fecha_inicio + timedelta(days=dias_anticipacion)
        
        fecha_venc_col = self._get_column('fecha_vencimiento')
        estado_col = self._get_column('estado')
        
        stmt = (
            select(PlanCuota)
            .where(
                and_(
                    fecha_venc_col >= fecha_inicio,
                    fecha_venc_col <= fecha_limite,
                    estado_col == EstadoCuota.pendiente
                )
            )
            .order_by(fecha_venc_col.asc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== GESTIÓN DE PAGOS ====================

    async def registrar_pago_cuota(
        self,
        cuota_id: int,
        monto_pagado: Decimal,
        pago_id: Optional[int] = None
    ) -> Optional[PlanCuota]:
        """
        Marca una cuota como pagada.
        
        Args:
            cuota_id: ID de la cuota
            monto_pagado: Monto del pago
            pago_id: ID del pago asociado (opcional)
            
        Returns:
            Cuota actualizada o None si no existe
        """
        cuota = await self.get(cuota_id)
        
        if not cuota:
            return None
        
        # ✅ Acceso seguro
        estado_actual: EstadoCuota = getattr(cuota, 'estado', EstadoCuota.pendiente)
        
        if estado_actual == EstadoCuota.pagado:
            raise ValueError(f"La cuota {cuota_id} ya está marcada como pagada")
        
        # ✅ Actualizar con setattr
        assert hasattr(cuota, 'estado'), "PlanCuota debe tener 'estado'"
        setattr(cuota, 'estado', EstadoCuota.pagado)
        
        assert hasattr(cuota, 'monto'), "PlanCuota debe tener 'monto'"
        setattr(cuota, 'monto', monto_pagado)
        
        assert hasattr(cuota, 'actualizado_en'), "PlanCuota debe tener 'actualizado_en'"
        setattr(cuota, 'actualizado_en', datetime.utcnow())
        
        if pago_id:
            assert hasattr(cuota, 'pago_id'), "PlanCuota debe tener 'pago_id'"
            setattr(cuota, 'pago_id', pago_id)
        
        await self.session.flush()
        
        return cuota

    async def anular_pago_cuota(
        self,
        cuota_id: int
    ) -> Optional[PlanCuota]:
        """
        Revierte el pago de una cuota (vuelve a pendiente o vencida).
        
        Args:
            cuota_id: ID de la cuota
            
        Returns:
            Cuota revertida o None si no existe
        """
        cuota = await self.get(cuota_id)
        
        if not cuota:
            return None
        
        # ✅ Acceso seguro
        estado_actual: EstadoCuota = getattr(cuota, 'estado', EstadoCuota.pendiente)
        
        if estado_actual != EstadoCuota.pagado:
            raise ValueError(f"La cuota {cuota_id} no está pagada")
        
        # Determinar nuevo estado según fecha
        fecha_vencimiento_val: date = getattr(cuota, 'fecha_vencimiento', date.today())
        
        if fecha_vencimiento_val < date.today():
            nuevo_estado = EstadoCuota.vencido
        else:
            nuevo_estado = EstadoCuota.pendiente
        
        # ✅ Actualizar con setattr
        assert hasattr(cuota, 'estado'), "PlanCuota debe tener 'estado'"
        setattr(cuota, 'estado', nuevo_estado)
        
        assert hasattr(cuota, 'actualizado_en'), "PlanCuota debe tener 'actualizado_en'"
        setattr(cuota, 'actualizado_en', datetime.utcnow())
        
        await self.session.flush()
        
        return cuota

    # ==================== ESTADÍSTICAS ====================

    async def calcular_estadisticas_plan(self, plan_pago_id: int) -> Dict[str, Any]:
        """
        Calcula estadísticas de cuotas de un plan.
        
        Returns:
            dict con {total_cuotas, pagadas, pendientes, vencidas, monto_total, monto_pagado}
        """
        id_col = self._get_column('id')
        estado_col = self._get_column('estado')
        monto_col = self._get_column('monto')
        plan_pago_id_col = self._get_column('plan_pago_id')
        
        stmt = (
            select(
                func.count(id_col),
                func.sum(case((estado_col == EstadoCuota.pagado, 1), else_=0)),
                func.sum(case((estado_col == EstadoCuota.pendiente, 1), else_=0)),
                func.sum(case((estado_col == EstadoCuota.vencido, 1), else_=0)),
                func.sum(monto_col),
                func.sum(case((estado_col == EstadoCuota.pagado, monto_col), else_=0))
            )
            .where(plan_pago_id_col == plan_pago_id)
        )
        
        result = await self.session.execute(stmt)
        row: Row[Tuple[int, int, int, int, Optional[Decimal], Optional[Decimal]]] = result.one()
        
        total: int = row[0]
        pagadas: int = row[1]
        pendientes: int = row[2]
        vencidas: int = row[3]
        monto_total: Optional[Decimal] = row[4]
        monto_pagado: Optional[Decimal] = row[5]
        
        monto_total_float: float = float(monto_total) if monto_total else 0.0
        monto_pagado_float: float = float(monto_pagado) if monto_pagado else 0.0
        
        return {
            'plan_pago_id': plan_pago_id,
            'total_cuotas': total,
            'pagadas': pagadas,
            'pendientes': pendientes,
            'vencidas': vencidas,
            'monto_total': monto_total_float,
            'monto_pagado': monto_pagado_float,
            'saldo_pendiente': monto_total_float - monto_pagado_float,
            'porcentaje_avance': round((monto_pagado_float / monto_total_float * 100) if monto_total_float > 0 else 0, 2)
        }

    async def obtener_cronograma_pagos(self, plan_pago_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene el cronograma completo de pagos (tabla de amortización).
        
        Returns:
            Lista de dicts con información de cada cuota
        """
        cuotas: List[PlanCuota] = await self.listar_por_plan(plan_pago_id)
        
        resultado: List[Dict[str, Any]] = []
        
        for cuota in cuotas:
            # ✅ Acceso seguro a atributos
            numero_cuota_val: int = getattr(cuota, 'numero_cuota', 0)
            monto_val: Decimal = getattr(cuota, 'monto', Decimal('0.00'))
            fecha_venc_val: date = getattr(cuota, 'fecha_vencimiento', date.today())
            estado_val: EstadoCuota = getattr(cuota, 'estado', EstadoCuota.pendiente)
            pago_id_val: Optional[int] = getattr(cuota, 'pago_id', None)
            
            # Calcular días vencido
            dias_vencido: int = 0
            if fecha_venc_val < date.today() and estado_val != EstadoCuota.pagado:
                dias_vencido = (date.today() - fecha_venc_val).days
            
            resultado.append({
                'numero_cuota': numero_cuota_val,
                'monto': float(monto_val),
                'fecha_vencimiento': fecha_venc_val.isoformat(),
                'estado': estado_val.value,
                'dias_vencido': dias_vencido,
                'pago_id': pago_id_val
            })
        
        return resultado

    # ==================== VALIDACIONES ====================

    async def verificar_plan_completo(self, plan_pago_id: int) -> bool:
        """
        Verifica si todas las cuotas de un plan están pagadas.
        
        Returns:
            True si todas están pagadas, False si hay pendientes
        """
        id_col = self._get_column('id')
        plan_pago_id_col = self._get_column('plan_pago_id')
        estado_col = self._get_column('estado')
        
        stmt = (
            select(func.count(id_col))
            .where(
                and_(
                    plan_pago_id_col == plan_pago_id,
                    estado_col != EstadoCuota.pagado
                )
            )
        )
        
        result = await self.session.execute(stmt)
        count: int = result.scalar_one()
        
        return count == 0
