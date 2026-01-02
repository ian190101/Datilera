# app/infrastructure/db/repositories/finanzas/categorias_pago_repo.py
from typing import Optional, List, Dict, Tuple, Any
from datetime import date
from decimal import Decimal
from sqlalchemy import select, func, and_, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import CategoriaPago


class CategoriasPagoRepository(BaseRepository[CategoriaPago]):
    """
    Repositorio para categorías de pago (tipos de ingresos).
    Gestiona categorías como mensualidad, inscripción, material, etc.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, CategoriaPago)

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
        col = getattr(CategoriaPago, name, None)
        assert col is not None, f"CategoriaPago no tiene atributo '{name}'"
        return col

    # ==================== CONSULTAS BÁSICAS ====================

    async def listar_por_sede(
        self, 
        sede_id: int,
        activas_solo: bool = True
    ) -> List[CategoriaPago]:
        """
        Lista categorías de pago de una sede.
        
        Args:
            sede_id: ID de la sede
            activas_solo: Si True, solo retorna categorías activas
        """
        sede_id_col = self._get_column('sede_id')
        stmt = select(CategoriaPago).where(sede_id_col == sede_id)
        
        if activas_solo:
            activa_col = self._get_column('activa')
            stmt = stmt.where(activa_col == True)
        
        nombre_col = self._get_column('nombre')
        stmt = stmt.order_by(nombre_col.asc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obtener_por_nombre(
        self, 
        sede_id: int, 
        nombre: str
    ) -> Optional[CategoriaPago]:
        """Busca categoría por nombre exacto en una sede."""
        sede_id_col = self._get_column('sede_id')
        nombre_col = self._get_column('nombre')
        
        stmt = select(CategoriaPago).where(
            and_(
                sede_id_col == sede_id,
                nombre_col == nombre
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def buscar_por_nombre_parcial(
        self,
        sede_id: int,
        nombre_parcial: str,
        activas_solo: bool = True
    ) -> List[CategoriaPago]:
        """Busca categorías que contengan el texto."""
        sede_id_col = self._get_column('sede_id')
        nombre_col = self._get_column('nombre')
        
        stmt = select(CategoriaPago).where(
            and_(
                sede_id_col == sede_id,
                nombre_col.ilike(f"%{nombre_parcial}%")
            )
        )
        
        if activas_solo:
            activa_col = self._get_column('activa')
            stmt = stmt.where(activa_col == True)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== GESTIÓN DE ESTADO ====================

    async def activar_categoria(self, categoria_id: int) -> Optional[CategoriaPago]:
        """Activa una categoría desactivada."""
        categoria = await self.get(categoria_id)
        
        if not categoria:
            return None
        
        # ✅ Usar setattr con assert previo
        assert hasattr(categoria, 'activa'), "Categoria debe tener atributo 'activa'"
        setattr(categoria, 'activa', True)
        
        await self.session.commit()
        await self.session.refresh(categoria)
        
        return categoria

    async def desactivar_categoria(self, categoria_id: int) -> Optional[CategoriaPago]:
        """
        Desactiva una categoría (soft delete).
        No permite eliminar si tiene pagos asociados.
        """
        categoria = await self.get(categoria_id)
        
        if not categoria:
            return None
        
        # Verificar si tiene pagos asociados
        tiene_pagos = await self.tiene_pagos_asociados(categoria_id)
        if tiene_pagos:
            # ✅ Acceso seguro con getattr
            nombre_cat: str = getattr(categoria, 'nombre', 'Desconocida')
            raise ValueError(
                f"No se puede desactivar la categoría '{nombre_cat}' "
                "porque tiene pagos asociados."
            )
        
        # ✅ Usar setattr con assert previo
        assert hasattr(categoria, 'activa'), "Categoria debe tener atributo 'activa'"
        setattr(categoria, 'activa', False)
        
        await self.session.commit()
        await self.session.refresh(categoria)
        
        return categoria

    # ==================== VALIDACIONES ====================

    async def verificar_nombre_duplicado(
        self,
        sede_id: int,
        nombre: str,
        excluir_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si existe una categoría con el mismo nombre.
        
        Args:
            sede_id: ID de la sede
            nombre: Nombre a verificar
            excluir_id: ID de categoría a excluir (para updates)
            
        Returns:
            True si existe duplicado, False si no
        """
        sede_id_col = self._get_column('sede_id')
        nombre_col = self._get_column('nombre')
        
        stmt = select(CategoriaPago).where(
            and_(
                sede_id_col == sede_id,
                nombre_col == nombre
            )
        )
        
        if excluir_id:
            id_col = self._get_column('id')
            stmt = stmt.where(id_col != excluir_id)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def tiene_pagos_asociados(self, categoria_id: int) -> bool:
        """Verifica si la categoría tiene pagos registrados."""
        from app.infrastructure.db.models.finanzas import Pago
        
        # ✅ Acceso seguro a columnas de Pago
        pago_id_col = getattr(Pago, 'id', None)
        assert pago_id_col is not None, "Pago debe tener atributo 'id'"
        
        pago_cat_col = getattr(Pago, 'categoria_pago_id', None)
        assert pago_cat_col is not None, "Pago debe tener atributo 'categoria_pago_id'"
        
        stmt = select(func.count(pago_id_col)).where(pago_cat_col == categoria_id)
        result = await self.session.execute(stmt)
        count: int = result.scalar_one()
        
        return count > 0

    # ==================== ESTADÍSTICAS ====================

    async def obtener_uso_categorias(
        self,
        sede_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene estadísticas de uso de cada categoría.
        
        Returns:
            Lista de dicts con {categoria_id, nombre, total_pagos, monto_total}
        """
        from app.infrastructure.db.models.finanzas import Pago
        
        # ✅ Acceso seguro a columnas
        cat_id_col = self._get_column('id')
        cat_nombre_col = self._get_column('nombre')
        cat_sede_col = self._get_column('sede_id')
        
        pago_id_col = getattr(Pago, 'id', None)
        assert pago_id_col is not None, "Pago debe tener 'id'"
        
        pago_cat_col = getattr(Pago, 'categoria_pago_id', None)
        assert pago_cat_col is not None, "Pago debe tener 'categoria_pago_id'"
        
        pago_monto_col = getattr(Pago, 'monto_pagado', None)
        assert pago_monto_col is not None, "Pago debe tener 'monto_pagado'"
        
        pago_fecha_col = getattr(Pago, 'fecha_pago', None)
        assert pago_fecha_col is not None, "Pago debe tener 'fecha_pago'"
        
        stmt = (
            select(
                cat_id_col,
                cat_nombre_col,
                func.count(pago_id_col),
                func.sum(pago_monto_col)
            )
            .outerjoin(Pago, pago_cat_col == cat_id_col)
            .where(cat_sede_col == sede_id)
        )
        
        if fecha_desde:
            stmt = stmt.where(pago_fecha_col >= fecha_desde)
        if fecha_hasta:
            stmt = stmt.where(pago_fecha_col <= fecha_hasta)
        
        stmt = stmt.group_by(
            cat_id_col, 
            cat_nombre_col
        ).order_by(
            func.sum(pago_monto_col).desc()
        )
        
        result = await self.session.execute(stmt)
        rows: List[Row[Tuple[int, str, int, Optional[Decimal]]]] = list(result.all())
        
        return [
            {
                'categoria_id': row[0],
                'nombre': row[1],
                'total_pagos': row[2],
                'monto_total': float(row[3]) if row[3] else 0.0
            }
            for row in rows
        ]

    async def obtener_categoria_mas_usada(self, sede_id: int) -> Optional[CategoriaPago]:
        """Obtiene la categoría con más pagos registrados."""
        from app.infrastructure.db.models.finanzas import Pago
        
        # ✅ Acceso seguro a columnas
        cat_id_col = self._get_column('id')
        cat_sede_col = self._get_column('sede_id')
        
        pago_id_col = getattr(Pago, 'id', None)
        assert pago_id_col is not None, "Pago debe tener 'id'"
        
        pago_cat_col = getattr(Pago, 'categoria_pago_id', None)
        assert pago_cat_col is not None, "Pago debe tener 'categoria_pago_id'"
        
        stmt = (
            select(CategoriaPago, func.count(pago_id_col))
            .join(Pago, pago_cat_col == cat_id_col)
            .where(cat_sede_col == sede_id)
            .group_by(cat_id_col)
            .order_by(func.count(pago_id_col).desc())
            .limit(1)
        )
        
        result = await self.session.execute(stmt)
        row: Optional[Row[Tuple[CategoriaPago, int]]] = result.first()
        
        return row[0] if row else None

    # ==================== MÉTODOS AUXILIARES ====================

    async def contar_activas(self, sede_id: int) -> int:
        """Cuenta categorías activas de una sede."""
        sede_id_col = self._get_column('sede_id')
        activa_col = self._get_column('activa')
        id_col = self._get_column('id')
        
        stmt = select(func.count(id_col)).where(
            and_(
                sede_id_col == sede_id,
                activa_col == True
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def obtener_todas_activas(self) -> List[CategoriaPago]:
        """Obtiene todas las categorías activas del sistema."""
        activa_col = self._get_column('activa')
        nombre_col = self._get_column('nombre')
        
        stmt = select(CategoriaPago).where(
            activa_col == True
        ).order_by(nombre_col.asc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
