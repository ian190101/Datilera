# app/infrastructure/db/repositories/finanzas/egresos_repo.py
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Egreso


class EgresosRepository(BaseRepository[Egreso]):
    """
    Repositorio para gestión de egresos (gastos) del sistema.
    Maneja registros de egresos operativos con soporte para anulaciones.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Egreso)

    # ==================== CONSULTAS BÁSICAS ====================

    async def listar_por_sede(
        self, 
        sede_id: int, 
        incluir_anulados: bool = False,
        limit: int = 100, 
        offset: int = 0
    ) -> List[Egreso]:
        """Lista egresos de una sede específica."""
        stmt = select(Egreso).where(Egreso.sede_id == sede_id)
        
        if not incluir_anulados:
            stmt = stmt.where(Egreso.anulado == False)
        
        stmt = stmt.order_by(Egreso.fecha_egreso.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def listar_por_sede_fecha(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date,
        incluir_anulados: bool = False,
        limit: int = 500,
        offset: int = 0
    ) -> List[Egreso]:
        """Lista egresos de una sede en un rango de fechas."""
        stmt = select(Egreso).where(
            and_(
                Egreso.sede_id == sede_id,
                Egreso.fecha_egreso >= fecha_desde,
                Egreso.fecha_egreso <= fecha_hasta
            )
        )
        
        if not incluir_anulados:
            stmt = stmt.where(Egreso.anulado == False)
        
        stmt = stmt.order_by(Egreso.fecha_egreso.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def obtener_por_comprobante(
        self, 
        numero_comprobante: str
    ) -> Optional[Egreso]:
        """Busca un egreso por número de comprobante."""
        stmt = select(Egreso).where(Egreso.numero_comprobante == numero_comprobante)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def obtener_con_relaciones(self, egreso_id: int) -> Optional[Egreso]:
        """Obtiene un egreso con todas sus relaciones cargadas."""
        stmt = (
            select(Egreso)
            .options(
                selectinload(Egreso.sede),
                selectinload(Egreso.categoria),
                selectinload(Egreso.usuario_registro),
                selectinload(Egreso.usuario_anulacion),
                selectinload(Egreso.libro_caja_item)
            )
            .where(Egreso.id == egreso_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ==================== ANULACIONES ====================

    async def anular_egreso(
        self,
        egreso_id: int,
        anulado_por_id: int,
        motivo: str
    ) -> Optional[Egreso]:
        """
        Anula un egreso existente.
        
        Args:
            egreso_id: ID del egreso a anular
            anulado_por_id: ID del usuario que anula
            motivo: Motivo de la anulación
            
        Returns:
            Egreso anulado o None si no existe
        """
        egreso = await self.get_by_id(egreso_id)
        
        if not egreso:
            return None
        
        if egreso.anulado:
            raise ValueError(f"El egreso {egreso_id} ya está anulado")
        
        egreso.anulado = True
        egreso.anulado_por = anulado_por_id
        egreso.anulado_en = datetime.utcnow()
        egreso.motivo_anulacion = motivo
        
        await self.session.commit()
        await self.session.refresh(egreso)
        
        return egreso

    async def listar_anulados(
        self,
        sede_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Egreso]:
        """Lista todos los egresos anulados con filtros opcionales."""
        stmt = select(Egreso).where(Egreso.anulado == True)
        
        if sede_id:
            stmt = stmt.where(Egreso.sede_id == sede_id)
        
        if fecha_desde:
            stmt = stmt.where(Egreso.anulado_en >= fecha_desde)
        
        if fecha_hasta:
            stmt = stmt.where(Egreso.anulado_en <= fecha_hasta)
        
        stmt = stmt.order_by(Egreso.anulado_en.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ==================== ESTADÍSTICAS Y REPORTES ====================

    async def calcular_total_por_categoria(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date,
        incluir_anulados: bool = False
    ) -> List[dict]:
        """
        Calcula el total de egresos agrupados por categoría.
        
        Returns:
            Lista de dicts con {categoria_id, categoria_nombre, total, cantidad}
        """
        from app.infrastructure.db.models.finanzas import CategoriaEgreso
        
        stmt = (
            select(
                CategoriaEgreso.id.label('categoria_id'),
                CategoriaEgreso.nombre.label('categoria_nombre'),
                func.sum(Egreso.monto).label('total'),
                func.count(Egreso.id).label('cantidad')
            )
            .join(Egreso, Egreso.categoria_egreso_id == CategoriaEgreso.id)
            .where(
                and_(
                    Egreso.sede_id == sede_id,
                    Egreso.fecha_egreso >= fecha_desde,
                    Egreso.fecha_egreso <= fecha_hasta
                )
            )
        )
        
        if not incluir_anulados:
            stmt = stmt.where(Egreso.anulado == False)
        
        stmt = stmt.group_by(CategoriaEgreso.id, CategoriaEgreso.nombre)
        
        result = await self.session.execute(stmt)
        
        return [
            {
                'categoria_id': row.categoria_id,
                'categoria_nombre': row.categoria_nombre,
                'total': float(row.total) if row.total else 0.0,
                'cantidad': row.cantidad
            }
            for row in result.all()
        ]

    async def calcular_egresos_por_mes(
        self,
        sede_id: int,
        año: int,
        incluir_anulados: bool = False
    ) -> List[dict]:
        """
        Calcula egresos agrupados por mes para un año específico.
        
        Returns:
            Lista de dicts con {mes, total_egresos, cantidad_egresos}
        """
        stmt = (
            select(
                extract('month', Egreso.fecha_egreso).label('mes'),
                func.sum(Egreso.monto).label('total_egresos'),
                func.count(Egreso.id).label('cantidad_egresos')
            )
            .where(
                and_(
                    Egreso.sede_id == sede_id,
                    extract('year', Egreso.fecha_egreso) == año
                )
            )
        )
        
        if not incluir_anulados:
            stmt = stmt.where(Egreso.anulado == False)
        
        stmt = stmt.group_by(extract('month', Egreso.fecha_egreso)).order_by('mes')
        
        result = await self.session.execute(stmt)
        
        return [
            {
                'mes': int(row.mes),
                'total_egresos': float(row.total_egresos) if row.total_egresos else 0.0,
                'cantidad_egresos': row.cantidad_egresos
            }
            for row in result.all()
        ]

    async def calcular_total_periodo(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date,
        incluir_anulados: bool = False
    ) -> Decimal:
        """Calcula el total de egresos en un periodo."""
        stmt = select(func.sum(Egreso.monto)).where(
            and_(
                Egreso.sede_id == sede_id,
                Egreso.fecha_egreso >= fecha_desde,
                Egreso.fecha_egreso <= fecha_hasta
            )
        )
        
        if not incluir_anulados:
            stmt = stmt.where(Egreso.anulado == False)
        
        result = await self.session.execute(stmt)
        total = result.scalar_one_or_none()
        
        return total if total else Decimal('0.00')

    # ==================== PROVEEDORES ====================

    async def listar_por_proveedor(
        self,
        proveedor: str,
        sede_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        incluir_anulados: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Egreso]:
        """Lista egresos filtrados por proveedor."""
        stmt = select(Egreso).where(Egreso.proveedor.ilike(f"%{proveedor}%"))
        
        if not incluir_anulados:
            stmt = stmt.where(Egreso.anulado == False)
        
        if sede_id:
            stmt = stmt.where(Egreso.sede_id == sede_id)
        
        if fecha_desde:
            stmt = stmt.where(Egreso.fecha_egreso >= fecha_desde)
        
        if fecha_hasta:
            stmt = stmt.where(Egreso.fecha_egreso <= fecha_hasta)
        
        stmt = stmt.order_by(Egreso.fecha_egreso.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def obtener_proveedores_frecuentes(
        self,
        sede_id: int,
        limit: int = 20
    ) -> List[dict]:
        """
        Obtiene los proveedores más frecuentes con totales.
        
        Returns:
            Lista de dicts con {proveedor, total_gastado, cantidad_egresos}
        """
        stmt = (
            select(
                Egreso.proveedor,
                func.sum(Egreso.monto).label('total_gastado'),
                func.count(Egreso.id).label('cantidad_egresos')
            )
            .where(
                and_(
                    Egreso.sede_id == sede_id,
                    Egreso.anulado == False,
                    Egreso.proveedor.isnot(None)
                )
            )
            .group_by(Egreso.proveedor)
            .order_by(func.sum(Egreso.monto).desc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        
        return [
            {
                'proveedor': row.proveedor,
                'total_gastado': float(row.total_gastado) if row.total_gastado else 0.0,
                'cantidad_egresos': row.cantidad_egresos
            }
            for row in result.all()
        ]

    # ==================== MÉTODOS DE PAGO ====================

    async def listar_por_metodo_pago(
        self,
        metodo_pago: str,
        sede_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        incluir_anulados: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Egreso]:
        """Lista egresos filtrados por método de pago."""
        stmt = select(Egreso).where(Egreso.metodo_pago == metodo_pago)
        
        if not incluir_anulados:
            stmt = stmt.where(Egreso.anulado == False)
        
        if sede_id:
            stmt = stmt.where(Egreso.sede_id == sede_id)
        
        if fecha_desde:
            stmt = stmt.where(Egreso.fecha_egreso >= fecha_desde)
        
        if fecha_hasta:
            stmt = stmt.where(Egreso.fecha_egreso <= fecha_hasta)
        
        stmt = stmt.order_by(Egreso.fecha_egreso.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ==================== VALIDACIONES ====================

    async def verificar_duplicado_comprobante(
        self,
        numero_comprobante: str,
        excluir_egreso_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si existe un comprobante duplicado.
        
        Args:
            numero_comprobante: Número a verificar
            excluir_egreso_id: ID de egreso a excluir de la búsqueda
            
        Returns:
            True si existe duplicado, False si no
        """
        if not numero_comprobante:
            return False
        
        stmt = select(Egreso).where(Egreso.numero_comprobante == numero_comprobante)
        
        if excluir_egreso_id:
            stmt = stmt.where(Egreso.id != excluir_egreso_id)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
