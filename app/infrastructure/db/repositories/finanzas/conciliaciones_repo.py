# app/infrastructure/db/repositories/finanzas/conciliaciones_repo.py
from typing import Optional, List, Dict, Tuple, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select, func, case, and_, or_, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Conciliacion


class ConciliacionesRepository(BaseRepository[Conciliacion]):
    """
    Repositorio para conciliaciones bancarias/financieras.
    Gestiona el proceso de verificación y match entre pagos y comprobantes.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Conciliacion)

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
        col = getattr(Conciliacion, name, None)
        assert col is not None, f"Conciliacion no tiene atributo '{name}'"
        return col

    def _get_relationship(self, name: str) -> Any:
        """
        Helper para obtener relación con tipo seguro.
        
        Args:
            name: Nombre de la relación
            
        Returns:
            Relación tipada
            
        Raises:
            AssertionError: Si la relación no existe
        """
        rel = getattr(Conciliacion, name, None)
        assert rel is not None, f"Conciliacion no tiene relación '{name}'"
        return rel

    # ==================== CONSULTAS BÁSICAS ====================

    async def obtener_por_pago(self, pago_id: int) -> List[Conciliacion]:
        """Obtiene todas las conciliaciones de un pago."""
        pago_id_col = self._get_column('pago_id')
        
        stmt = select(Conciliacion).where(pago_id_col == pago_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obtener_por_comprobante(self, comprobante_id: int) -> List[Conciliacion]:
        """Obtiene todas las conciliaciones de un comprobante."""
        comprobante_id_col = self._get_column('comprobante_id')
        
        stmt = select(Conciliacion).where(comprobante_id_col == comprobante_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obtener_con_relaciones(self, conciliacion_id: int) -> Optional[Conciliacion]:
        """Obtiene conciliación con pago, comprobante y usuario."""
        id_col = self._get_column('id')
        
        # ✅ Obtener relaciones con helper
        pago_rel = self._get_relationship('pago')
        comprobante_rel = self._get_relationship('comprobante')
        usuario_rel = self._get_relationship('usuario_conciliador')
        
        stmt = (
            select(Conciliacion)
            .options(
                selectinload(pago_rel),
                selectinload(comprobante_rel),
                selectinload(usuario_rel)
            )
            .where(id_col == conciliacion_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def listar_por_fecha(
        self,
        fecha_desde: date,
        fecha_hasta: date,
        conciliado: Optional[bool] = None,
        limit: int = 200,
        offset: int = 0
    ) -> List[Conciliacion]:
        """
        Lista conciliaciones en un rango de fechas.
        
        Args:
            fecha_desde: Fecha inicial
            fecha_hasta: Fecha final
            conciliado: Si True filtra conciliadas, si False pendientes, si None todas
        """
        fecha_conciliacion_col = self._get_column('fecha_conciliacion')
        conciliado_col = self._get_column('conciliado')
        
        stmt = select(Conciliacion).where(
            and_(
                fecha_conciliacion_col >= fecha_desde,
                fecha_conciliacion_col <= fecha_hasta
            )
        )
        
        if conciliado is not None:
            stmt = stmt.where(conciliado_col == conciliado)
        
        stmt = stmt.order_by(fecha_conciliacion_col.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== GESTIÓN DE CONCILIACIONES ====================

    async def crear_conciliacion(
        self,
        pago_id: int,
        monto_conciliado: Decimal,
        fecha_conciliacion: date,
        conciliado_por_id: int,
        comprobante_id: Optional[int] = None,
        observaciones: Optional[str] = None
    ) -> Conciliacion:
        """
        Crea una nueva conciliación.
        
        Args:
            pago_id: ID del pago
            monto_conciliado: Monto verificado
            fecha_conciliacion: Fecha de la conciliación
            conciliado_por_id: ID del usuario que concilia
            comprobante_id: ID del comprobante asociado (opcional)
            observaciones: Notas adicionales (opcional)
            
        Returns:
            Conciliación creada
        """
        conciliacion = Conciliacion(
            pago_id=pago_id,
            comprobante_id=comprobante_id,
            monto_conciliado=monto_conciliado,
            fecha_conciliacion=fecha_conciliacion,
            conciliado=False,
            conciliado_por=conciliado_por_id,
            observaciones=observaciones
        )
        
        self.session.add(conciliacion)
        await self.session.commit()
        await self.session.refresh(conciliacion)
        
        return conciliacion

    async def marcar_como_conciliado(
        self,
        conciliacion_id: int,
        observaciones_adicionales: Optional[str] = None
    ) -> Optional[Conciliacion]:
        """
        Marca una conciliación como completada/verificada.
        
        Args:
            conciliacion_id: ID de la conciliación
            observaciones_adicionales: Notas al conciliar (opcional)
            
        Returns:
            Conciliación actualizada o None si no existe
        """
        conciliacion = await self.get(conciliacion_id)
        
        if not conciliacion:
            return None
        
        conciliado_actual: bool = getattr(conciliacion, 'conciliado', False)
        
        if conciliado_actual:
            raise ValueError(f"La conciliación {conciliacion_id} ya está marcada como conciliada")
        
        assert hasattr(conciliacion, 'conciliado'), "Conciliacion debe tener 'conciliado'"
        setattr(conciliacion, 'conciliado', True)
        
        if observaciones_adicionales:
            observaciones_actuales: Optional[str] = getattr(conciliacion, 'observaciones', None)
            
            if observaciones_actuales:
                nueva_observacion = observaciones_actuales + f"\n[Conciliado]: {observaciones_adicionales}"
            else:
                nueva_observacion = f"[Conciliado]: {observaciones_adicionales}"
            
            assert hasattr(conciliacion, 'observaciones'), "Conciliacion debe tener 'observaciones'"
            setattr(conciliacion, 'observaciones', nueva_observacion)
        
        await self.session.commit()
        await self.session.refresh(conciliacion)
        
        return conciliacion

    async def reversar_conciliacion(
        self,
        conciliacion_id: int,
        motivo: str
    ) -> Optional[Conciliacion]:
        """
        Revierte una conciliación (marca como no conciliada).
        
        Args:
            conciliacion_id: ID de la conciliación
            motivo: Razón de la reversión
            
        Returns:
            Conciliación revertida o None si no existe
        """
        conciliacion = await self.get(conciliacion_id)
        
        if not conciliacion:
            return None
        
        conciliado_actual: bool = getattr(conciliacion, 'conciliado', False)
        
        if not conciliado_actual:
            raise ValueError(f"La conciliación {conciliacion_id} no está marcada como conciliada")
        
        assert hasattr(conciliacion, 'conciliado'), "Conciliacion debe tener 'conciliado'"
        setattr(conciliacion, 'conciliado', False)
        
        observacion_reversion = f"\n[REVERTIDO {datetime.utcnow().isoformat()}]: {motivo}"
        observaciones_actuales: Optional[str] = getattr(conciliacion, 'observaciones', None)
        
        if observaciones_actuales:
            nueva_observacion = observaciones_actuales + observacion_reversion
        else:
            nueva_observacion = observacion_reversion
        
        assert hasattr(conciliacion, 'observaciones'), "Conciliacion debe tener 'observaciones'"
        setattr(conciliacion, 'observaciones', nueva_observacion)
        
        await self.session.commit()
        await self.session.refresh(conciliacion)
        
        return conciliacion

    # ==================== ESTADÍSTICAS Y REPORTES ====================

    async def obtener_resumen_periodo(
        self,
        fecha_desde: date,
        fecha_hasta: date
    ) -> Dict[str, Any]:
        """
        Resumen de conciliaciones en un periodo.
        
        Returns:
            dict con {total_conciliaciones, conciliadas, pendientes, monto_conciliado, monto_pendiente}
        """
        id_col = self._get_column('id')
        conciliado_col = self._get_column('conciliado')
        monto_col = self._get_column('monto_conciliado')
        fecha_col = self._get_column('fecha_conciliacion')
        
        stmt = (
            select(
                func.count(id_col),
                func.sum(case((conciliado_col == True, 1), else_=0)),
                func.sum(case((conciliado_col == False, 1), else_=0)),
                func.sum(case((conciliado_col == True, monto_col), else_=0)),
                func.sum(case((conciliado_col == False, monto_col), else_=0))
            )
            .where(
                and_(
                    fecha_col >= fecha_desde,
                    fecha_col <= fecha_hasta
                )
            )
        )
        
        result = await self.session.execute(stmt)
        row: Row[Tuple[int, int, int, Optional[Decimal], Optional[Decimal]]] = result.one()
        
        total: int = row[0]
        conciliadas: int = row[1]
        pendientes: int = row[2]
        monto_conciliado: Optional[Decimal] = row[3]
        monto_pendiente: Optional[Decimal] = row[4]
        
        return {
            'total_conciliaciones': total,
            'conciliadas': conciliadas,
            'pendientes': pendientes,
            'monto_conciliado': float(monto_conciliado) if monto_conciliado else 0.0,
            'monto_pendiente': float(monto_pendiente) if monto_pendiente else 0.0,
            'porcentaje_conciliado': round((conciliadas / total * 100) if total > 0 else 0, 2)
        }

    async def listar_pendientes_antiguos(
        self,
        dias_antiguedad: int = 30,
        limit: int = 50
    ) -> List[Conciliacion]:
        """
        Lista conciliaciones pendientes con más de X días de antigüedad.
        
        Args:
            dias_antiguedad: Días mínimos de antigüedad
            limit: Límite de resultados
            
        Returns:
            Lista de conciliaciones pendientes antiguas
        """
        from datetime import timedelta
        
        fecha_limite = date.today() - timedelta(days=dias_antiguedad)
        
        conciliado_col = self._get_column('conciliado')
        fecha_col = self._get_column('fecha_conciliacion')
        
        stmt = (
            select(Conciliacion)
            .where(
                and_(
                    conciliado_col == False,
                    fecha_col <= fecha_limite
                )
            )
            .order_by(fecha_col.asc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obtener_diferencias_monto(
        self,
        tolerancia: Decimal = Decimal('0.01')
    ) -> List[Dict[str, Any]]:
        """
        Encuentra conciliaciones donde el monto conciliado difiere del monto del pago.
        
        Args:
            tolerancia: Diferencia mínima aceptable (default 0.01)
            
        Returns:
            Lista de dicts con {conciliacion_id, pago_id, monto_pago, monto_conciliado, diferencia}
        """
        from app.infrastructure.db.models.finanzas import Pago
        
        concil_id_col = self._get_column('id')
        concil_pago_col = self._get_column('pago_id')
        concil_monto_col = self._get_column('monto_conciliado')
        
        pago_id_col = getattr(Pago, 'id', None)
        assert pago_id_col is not None, "Pago debe tener 'id'"
        
        pago_monto_col = getattr(Pago, 'monto_pagado', None)
        assert pago_monto_col is not None, "Pago debe tener 'monto_pagado'"
        
        stmt = (
            select(
                concil_id_col,
                concil_pago_col,
                pago_monto_col,
                concil_monto_col,
                (pago_monto_col - concil_monto_col)
            )
            .join(Pago, pago_id_col == concil_pago_col)
            .where(
                func.abs(pago_monto_col - concil_monto_col) > tolerancia
            )
            .order_by(func.abs(pago_monto_col - concil_monto_col).desc())
        )
        
        result = await self.session.execute(stmt)
        rows: List[Row[Tuple[int, int, Decimal, Decimal, Decimal]]] = list(result.all())
        
        return [
            {
                'conciliacion_id': row[0],
                'pago_id': row[1],
                'monto_pago': float(row[2]),
                'monto_conciliado': float(row[3]),
                'diferencia': float(row[4]),
                'diferencia_abs': abs(float(row[4]))
            }
            for row in rows
        ]

    # ==================== VALIDACIONES ====================

    async def verificar_pago_conciliado(self, pago_id: int) -> bool:
        """
        Verifica si un pago tiene al menos una conciliación completada.
        
        Returns:
            True si el pago está conciliado, False si no
        """
        id_col = self._get_column('id')
        pago_id_col = self._get_column('pago_id')
        conciliado_col = self._get_column('conciliado')
        
        stmt = (
            select(func.count(id_col))
            .where(
                and_(
                    pago_id_col == pago_id,
                    conciliado_col == True
                )
            )
        )
        
        result = await self.session.execute(stmt)
        count: int = result.scalar_one()
        
        return count > 0

    async def obtener_tasa_conciliacion_usuario(
        self,
        usuario_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas de conciliación de un usuario.
        
        Returns:
            dict con {total_procesadas, conciliadas, tasa_exito}
        """
        id_col = self._get_column('id')
        conciliado_col = self._get_column('conciliado')
        conciliado_por_col = self._get_column('conciliado_por')
        fecha_col = self._get_column('fecha_conciliacion')
        
        stmt = (
            select(
                func.count(id_col),
                func.sum(case((conciliado_col == True, 1), else_=0))
            )
            .where(conciliado_por_col == usuario_id)
        )
        
        if fecha_desde:
            stmt = stmt.where(fecha_col >= fecha_desde)
        if fecha_hasta:
            stmt = stmt.where(fecha_col <= fecha_hasta)
        
        result = await self.session.execute(stmt)
        row: Row[Tuple[int, int]] = result.one()
        
        total: int = row[0]
        conciliadas: int = row[1]
        tasa_exito: float = (conciliadas / total * 100) if total > 0 else 0
        
        return {
            'usuario_id': usuario_id,
            'total_procesadas': total,
            'conciliadas': conciliadas,
            'pendientes': total - conciliadas,
            'tasa_exito': round(tasa_exito, 2)
        }
