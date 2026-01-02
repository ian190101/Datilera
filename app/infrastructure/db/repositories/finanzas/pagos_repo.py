# app/infrastructure/db/repositories/finanzas/pagos_repo.py
from typing import Optional, List, Dict, Tuple, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select, func, and_, extract, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Pago


class PagosRepository(BaseRepository[Pago]):
    """
    Repositorio para gestión de pagos (ingresos) del sistema.
    Maneja registros de pagos de alumnos con soporte para anulaciones.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Pago)

    # ==================== HELPERS INTERNOS ====================

    def _get_column(self, name: str) -> InstrumentedAttribute[Any]:
        """Helper para obtener columna con tipo seguro."""
        col = getattr(Pago, name, None)
        assert col is not None, f"Pago no tiene atributo '{name}'"
        return col

    def _get_relationship(self, name: str) -> Any:
        """Helper para obtener relación con tipo seguro."""
        rel = getattr(Pago, name, None)
        assert rel is not None, f"Pago no tiene relación '{name}'"
        return rel

    # ==================== CONSULTAS BÁSICAS ====================

    async def listar_por_alumno(
        self, 
        alumno_id: int, 
        incluir_anulados: bool = False,
        limit: int = 100, 
        offset: int = 0
    ) -> List[Pago]:
        """Lista pagos de un alumno específico."""
        alumno_id_col = self._get_column('alumno_id')
        anulado_col = self._get_column('anulado')
        fecha_pago_col = self._get_column('fecha_pago')
        
        stmt = select(Pago).where(alumno_id_col == alumno_id)
        
        if not incluir_anulados:
            stmt = stmt.where(anulado_col == False)
        
        stmt = stmt.order_by(fecha_pago_col.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def listar_por_sede_fecha(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date,
        incluir_anulados: bool = False,
        limit: int = 500,
        offset: int = 0
    ) -> List[Pago]:
        """Lista pagos de una sede en un rango de fechas."""
        from app.infrastructure.db.models.alumnos import Alumno
        
        fecha_pago_col = self._get_column('fecha_pago')
        anulado_col = self._get_column('anulado')
        alumno_id_col = self._get_column('alumno_id')
        
        # ✅ Columnas de Alumno
        alumno_id_col_alumno = getattr(Alumno, 'id', None)
        assert alumno_id_col_alumno is not None, "Alumno debe tener 'id'"
        
        alumno_sede_col = getattr(Alumno, 'sede_id', None)
        assert alumno_sede_col is not None, "Alumno debe tener 'sede_id'"
        
        stmt = (
            select(Pago)
            .join(Alumno, alumno_id_col == alumno_id_col_alumno)
            .where(
                and_(
                    alumno_sede_col == sede_id,
                    fecha_pago_col >= fecha_desde,
                    fecha_pago_col <= fecha_hasta
                )
            )
        )
        
        if not incluir_anulados:
            stmt = stmt.where(anulado_col == False)
        
        stmt = stmt.order_by(fecha_pago_col.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obtener_por_comprobante(
        self, 
        numero_comprobante: str
    ) -> Optional[Pago]:
        """Busca un pago por número de comprobante."""
        numero_comp_col = self._get_column('numero_comprobante')
        
        stmt = select(Pago).where(numero_comp_col == numero_comprobante)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def obtener_con_relaciones(self, pago_id: int) -> Optional[Pago]:
        """Obtiene un pago con todas sus relaciones cargadas."""
        id_col = self._get_column('id')
        
        # ✅ Obtener relaciones con helper
        alumno_rel = self._get_relationship('alumno')
        categoria_rel = self._get_relationship('categoria_pago')
        usuario_reg_rel = self._get_relationship('usuario_registro')
        usuario_anul_rel = self._get_relationship('usuario_anulacion')
        libro_caja_rel = self._get_relationship('libro_caja_items')
        
        stmt = (
            select(Pago)
            .options(
                selectinload(alumno_rel),
                selectinload(categoria_rel),
                selectinload(usuario_reg_rel),
                selectinload(usuario_anul_rel),
                selectinload(libro_caja_rel)
            )
            .where(id_col == pago_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ==================== ANULACIONES ====================

    async def anular_pago(
        self,
        pago_id: int,
        anulado_por_id: int,
        motivo: str
    ) -> Optional[Pago]:
        """Anula un pago existente."""
        pago = await self.get(pago_id)
        
        if not pago:
            return None
        
        anulado_actual: bool = getattr(pago, 'anulado', False)
        
        if anulado_actual:
            raise ValueError(f"El pago {pago_id} ya está anulado")
        
        assert hasattr(pago, 'anulado'), "Pago debe tener 'anulado'"
        setattr(pago, 'anulado', True)
        
        assert hasattr(pago, 'anulado_por'), "Pago debe tener 'anulado_por'"
        setattr(pago, 'anulado_por', anulado_por_id)
        
        assert hasattr(pago, 'anulado_en'), "Pago debe tener 'anulado_en'"
        setattr(pago, 'anulado_en', datetime.utcnow())
        
        assert hasattr(pago, 'motivo_anulacion'), "Pago debe tener 'motivo_anulacion'"
        setattr(pago, 'motivo_anulacion', motivo)
        
        await self.session.flush()
        
        return pago

    async def listar_anulados(
        self,
        sede_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Pago]:
        """Lista todos los pagos anulados con filtros opcionales."""
        from app.infrastructure.db.models.alumnos import Alumno
        
        anulado_col = self._get_column('anulado')
        anulado_en_col = self._get_column('anulado_en')
        
        stmt = select(Pago).where(anulado_col == True)
        
        if sede_id:
            alumno_id_col = self._get_column('alumno_id')
            
            alumno_id_col_alumno = getattr(Alumno, 'id', None)
            assert alumno_id_col_alumno is not None, "Alumno debe tener 'id'"
            
            alumno_sede_col = getattr(Alumno, 'sede_id', None)
            assert alumno_sede_col is not None, "Alumno debe tener 'sede_id'"
            
            stmt = stmt.join(Alumno, alumno_id_col == alumno_id_col_alumno).where(alumno_sede_col == sede_id)
        
        if fecha_desde:
            stmt = stmt.where(anulado_en_col >= fecha_desde)
        
        if fecha_hasta:
            stmt = stmt.where(anulado_en_col <= fecha_hasta)
        
        stmt = stmt.order_by(anulado_en_col.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== ESTADÍSTICAS Y REPORTES ====================

    async def calcular_total_por_categoria(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date,
        incluir_anulados: bool = False
    ) -> List[Dict[str, Any]]:
        """Calcula el total de pagos agrupados por categoría."""
        from app.infrastructure.db.models.finanzas import CategoriaPago
        from app.infrastructure.db.models.alumnos import Alumno
        
        pago_id_col = self._get_column('id')
        pago_monto_col = self._get_column('monto_pagado')
        pago_categoria_col = self._get_column('categoria_pago_id')
        pago_fecha_col = self._get_column('fecha_pago')
        pago_anulado_col = self._get_column('anulado')
        pago_alumno_col = self._get_column('alumno_id')
        
        cat_id_col = getattr(CategoriaPago, 'id', None)
        assert cat_id_col is not None, "CategoriaPago debe tener 'id'"
        
        cat_nombre_col = getattr(CategoriaPago, 'nombre', None)
        assert cat_nombre_col is not None, "CategoriaPago debe tener 'nombre'"
        
        alumno_id_col = getattr(Alumno, 'id', None)
        assert alumno_id_col is not None, "Alumno debe tener 'id'"
        
        alumno_sede_col = getattr(Alumno, 'sede_id', None)
        assert alumno_sede_col is not None, "Alumno debe tener 'sede_id'"
        
        stmt = (
            select(
                cat_id_col,
                cat_nombre_col,
                func.sum(pago_monto_col),
                func.count(pago_id_col)
            )
            .join(CategoriaPago, pago_categoria_col == cat_id_col)
            .join(Alumno, pago_alumno_col == alumno_id_col)
            .where(
                and_(
                    alumno_sede_col == sede_id,
                    pago_fecha_col >= fecha_desde,
                    pago_fecha_col <= fecha_hasta
                )
            )
        )
        
        if not incluir_anulados:
            stmt = stmt.where(pago_anulado_col == False)
        
        stmt = stmt.group_by(cat_id_col, cat_nombre_col)
        
        result = await self.session.execute(stmt)
        rows: List[Row[Tuple[int, str, Optional[Decimal], int]]] = list(result.all())
        
        return [
            {
                'categoria_id': row[0],
                'categoria_nombre': row[1],
                'total': float(row[2]) if row[2] else 0.0,
                'cantidad': row[3]
            }
            for row in rows
        ]

    async def calcular_ingresos_por_mes(
        self,
        sede_id: int,
        año: int,
        incluir_anulados: bool = False
    ) -> List[Dict[str, Any]]:
        """Calcula ingresos agrupados por mes para un año específico."""
        from app.infrastructure.db.models.alumnos import Alumno
        
        pago_id_col = self._get_column('id')
        pago_monto_col = self._get_column('monto_pagado')
        pago_fecha_col = self._get_column('fecha_pago')
        pago_anulado_col = self._get_column('anulado')
        pago_alumno_col = self._get_column('alumno_id')
        
        alumno_id_col = getattr(Alumno, 'id', None)
        assert alumno_id_col is not None, "Alumno debe tener 'id'"
        
        alumno_sede_col = getattr(Alumno, 'sede_id', None)
        assert alumno_sede_col is not None, "Alumno debe tener 'sede_id'"
        
        stmt = (
            select(
                extract('month', pago_fecha_col),
                func.sum(pago_monto_col),
                func.count(pago_id_col)
            )
            .join(Alumno, pago_alumno_col == alumno_id_col)
            .where(
                and_(
                    alumno_sede_col == sede_id,
                    extract('year', pago_fecha_col) == año
                )
            )
        )
        
        if not incluir_anulados:
            stmt = stmt.where(pago_anulado_col == False)
        
        stmt = stmt.group_by(extract('month', pago_fecha_col)).order_by(extract('month', pago_fecha_col))
        
        result = await self.session.execute(stmt)
        rows: List[Row[Tuple[int, Optional[Decimal], int]]] = list(result.all())
        
        return [
            {
                'mes': row[0],
                'total_ingresos': float(row[1]) if row[1] else 0.0,
                'cantidad_pagos': row[2]
            }
            for row in rows
        ]

    async def calcular_total_periodo(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date,
        incluir_anulados: bool = False
    ) -> Decimal:
        """Calcula el total de ingresos en un periodo."""
        from app.infrastructure.db.models.alumnos import Alumno
        
        pago_monto_col = self._get_column('monto_pagado')
        pago_fecha_col = self._get_column('fecha_pago')
        pago_anulado_col = self._get_column('anulado')
        pago_alumno_col = self._get_column('alumno_id')
        
        alumno_id_col = getattr(Alumno, 'id', None)
        assert alumno_id_col is not None, "Alumno debe tener 'id'"
        
        alumno_sede_col = getattr(Alumno, 'sede_id', None)
        assert alumno_sede_col is not None, "Alumno debe tener 'sede_id'"
        
        stmt = (
            select(func.sum(pago_monto_col))
            .join(Alumno, pago_alumno_col == alumno_id_col)
            .where(
                and_(
                    alumno_sede_col == sede_id,
                    pago_fecha_col >= fecha_desde,
                    pago_fecha_col <= fecha_hasta
                )
            )
        )
        
        if not incluir_anulados:
            stmt = stmt.where(pago_anulado_col == False)
        
        result = await self.session.execute(stmt)
        total: Optional[Decimal] = result.scalar_one_or_none()
        
        return total if total else Decimal('0.00')

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
    ) -> List[Pago]:
        """Lista pagos filtrados por método de pago."""
        from app.infrastructure.db.models.alumnos import Alumno
        
        metodo_pago_col = self._get_column('metodo_pago')
        anulado_col = self._get_column('anulado')
        fecha_pago_col = self._get_column('fecha_pago')
        
        stmt = select(Pago).where(metodo_pago_col == metodo_pago)
        
        if not incluir_anulados:
            stmt = stmt.where(anulado_col == False)
        
        if sede_id:
            pago_alumno_col = self._get_column('alumno_id')
            
            alumno_id_col = getattr(Alumno, 'id', None)
            assert alumno_id_col is not None, "Alumno debe tener 'id'"
            
            alumno_sede_col = getattr(Alumno, 'sede_id', None)
            assert alumno_sede_col is not None, "Alumno debe tener 'sede_id'"
            
            stmt = stmt.join(Alumno, pago_alumno_col == alumno_id_col).where(alumno_sede_col == sede_id)
        
        if fecha_desde:
            stmt = stmt.where(fecha_pago_col >= fecha_desde)
        
        if fecha_hasta:
            stmt = stmt.where(fecha_pago_col <= fecha_hasta)
        
        stmt = stmt.order_by(fecha_pago_col.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== VALIDACIONES ====================

    async def verificar_duplicado_comprobante(
        self,
        numero_comprobante: str,
        excluir_pago_id: Optional[int] = None
    ) -> bool:
        """Verifica si existe un comprobante duplicado."""
        if not numero_comprobante:
            return False
        
        numero_comp_col = self._get_column('numero_comprobante')
        id_col = self._get_column('id')
        
        stmt = select(Pago).where(numero_comp_col == numero_comprobante)
        
        if excluir_pago_id:
            stmt = stmt.where(id_col != excluir_pago_id)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
