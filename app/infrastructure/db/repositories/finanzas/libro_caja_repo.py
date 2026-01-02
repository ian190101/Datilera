# app/infrastructure/db/repositories/finanzas/libro_caja_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.infrastructure.db.repositories.base import BaseRepository
from typing import Optional, List, Tuple, Any
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.orm.attributes import InstrumentedAttribute
from app.infrastructure.db.models.finanzas import LibroCaja
from app.infrastructure.db.models.finanzas import LibroCaja as LibroCajaModel
from app.kernel.domain.finanzas import LibroCaja, TipoMovimiento

class LibroCajaRepository(BaseRepository[LibroCaja]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LibroCaja)

    async def obtener_por_id(self, movimiento_id: int) -> Optional[LibroCaja]:
        stmt = select(LibroCajaModel).where(LibroCajaModel.id == movimiento_id)
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        return None if m is None else self._to_entity(m)

    async def listar_por_sede_y_periodo(
        self, sede_id: int, fecha_inicio: date, fecha_fin: date, tipo: Optional[TipoMovimiento] = None
    ) -> List[LibroCaja]:
        stmt = select(LibroCajaModel).where(
            LibroCajaModel.sede_id == sede_id,
            LibroCajaModel.fecha >= fecha_inicio,
            LibroCajaModel.fecha <= fecha_fin,
        )
        if tipo is not None:
            stmt = stmt.where(LibroCajaModel.tipo == tipo.value)
        stmt = stmt.order_by(LibroCajaModel.fecha.desc(), LibroCajaModel.id.desc())
        res = await self.session.execute(stmt)
        return [self._to_entity(x) for x in res.scalars().all()]

    async def obtener_saldo_actual(self, sede_id: int) -> Decimal:
        stmt = (
            select(LibroCajaModel.saldo_acumulado)
            .where(LibroCajaModel.sede_id == sede_id)
            .order_by(LibroCajaModel.fecha.desc(), LibroCajaModel.id.desc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        v = res.scalar_one_or_none()
        return Decimal(str(v)) if v is not None else Decimal("0.0")

    async def calcular_totales_periodo(
        self, sede_id: int, fecha_inicio: date, fecha_fin: date
    ) -> Tuple[Decimal, Decimal, Decimal]:
        ingresos_q = select(func.coalesce(func.sum(LibroCajaModel.monto), 0)).where(
            LibroCajaModel.sede_id == sede_id,
            LibroCajaModel.fecha >= fecha_inicio,
            LibroCajaModel.fecha <= fecha_fin,
            LibroCajaModel.tipo == "ingreso",
        )
        egresos_q = select(func.coalesce(func.sum(LibroCajaModel.monto), 0)).where(
            LibroCajaModel.sede_id == sede_id,
            LibroCajaModel.fecha >= fecha_inicio,
            LibroCajaModel.fecha <= fecha_fin,
            LibroCajaModel.tipo == "egreso",
        )
        ing = (await self.session.execute(ingresos_q)).scalar_one()
        egr = (await self.session.execute(egresos_q)).scalar_one()
        ing_d = Decimal(str(ing))
        egr_d = Decimal(str(egr))
        return ing_d, egr_d, ing_d - egr_d

    async def existe_egreso_por_pago(self, pago_id: int) -> bool:
        stmt = select(func.count()).where(
            LibroCajaModel.pago_id == pago_id,
            LibroCajaModel.tipo == "egreso",
        )
        res = await self.session.execute(stmt)
        return (res.scalar_one() or 0) > 0

    async def existe_movimiento_por_referencia(self, sede_id: int, referencia: str) -> bool:
        stmt = select(func.count()).where(
            LibroCajaModel.sede_id == sede_id,
            LibroCajaModel.referencia == referencia,
        )
        res = await self.session.execute(stmt)
        return (res.scalar_one() or 0) > 0

    def _to_entity(self, m: LibroCajaModel) -> LibroCaja:
        return LibroCaja(
            id=m.id,
            sede_id=m.sede_id,
            fecha=m.fecha,
            tipo=TipoMovimiento(m.tipo),
            categoria_pago_id=m.categoria_pago_id,
            categoria_egreso_id=m.categoria_egreso_id,
            pago_id=m.pago_id,
            monto=Decimal(str(m.monto)),
            saldo_acumulado=Decimal(str(m.saldo_acumulado)) if m.saldo_acumulado is not None else None,
            concepto=m.concepto,
            referencia=m.referencia,
            usuario_registro_id=m.usuario_registro_id,
            creado_en=m.creado_en,
        )
    
     # ==================== HELPERS INTERNOS ====================

    def _get_column(self, name: str) -> InstrumentedAttribute[Any]:
        """Helper para obtener columna con tipo seguro."""
        col = getattr(LibroCaja, name, None)
        assert col is not None, f"LibroCaja no tiene atributo '{name}'"
        return col

    def _get_relationship(self, name: str) -> Any:
        """Helper para obtener relación con tipo seguro."""
        rel = getattr(LibroCaja, name, None)
        assert rel is not None, f"LibroCaja no tiene relación '{name}'"
        return rel

    # ==================== REGISTRO DE MOVIMIENTOS ====================

    async def registrar_ingreso(
        self,
        monto: Decimal,
        fecha: datetime,
        registrado_por_id: int,
        observaciones: str,
        pago_id: Optional[int] = None,
        sede_id: Optional[int] = None
    ) -> LibroCaja:
        """
        Registra un ingreso en el libro de caja.
        
        Args:
            monto: Monto del ingreso
            fecha: Fecha del movimiento
            registrado_por_id: ID del usuario que registra
            observaciones: Descripción del movimiento
            pago_id: ID del pago asociado (opcional)
            sede_id: ID de la sede (opcional)
            
        Returns:
            Movimiento registrado
        """
        movimiento = LibroCaja(
            tipo_movimiento='ingreso',
            monto=monto,
            fecha_movimiento=fecha,
            pago_id=pago_id,
            egreso_id=None,
            sede_id=sede_id,
            observaciones=observaciones,
            registrado_por=registrado_por_id,
            creado_en=datetime.utcnow()
        )
        
        self.session.add(movimiento)
        await self.session.flush()
        
        return movimiento

    async def registrar_egreso(
        self,
        monto: Decimal,
        fecha: datetime,
        registrado_por_id: int,
        observaciones: str,
        egreso_id: Optional[int] = None,
        sede_id: Optional[int] = None
    ) -> LibroCaja:
        """
        Registra un egreso en el libro de caja.
        
        Args:
            monto: Monto del egreso
            fecha: Fecha del movimiento
            registrado_por_id: ID del usuario que registra
            observaciones: Descripción del movimiento
            egreso_id: ID del egreso asociado (opcional)
            sede_id: ID de la sede (opcional)
            
        Returns:
            Movimiento registrado
        """
        movimiento = LibroCaja(
            tipo_movimiento='egreso',
            monto=monto,
            fecha_movimiento=fecha,
            pago_id=None,
            egreso_id=egreso_id,
            sede_id=sede_id,
            observaciones=observaciones,
            registrado_por=registrado_por_id,
            creado_en=datetime.utcnow()
        )
        
        self.session.add(movimiento)
        await self.session.flush()
        
        return movimiento
