# app/infrastructure/db/repositories/finanzas/comprobantes_repo.py
from typing import Optional, List, Any
from datetime import date
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Comprobante


class ComprobantesRepository(BaseRepository[Comprobante]):
    """
    Repositorio para comprobantes de pago.
    Gestiona documentos como facturas, recibos, etc.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Comprobante)

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
        col = getattr(Comprobante, name, None)
        assert col is not None, f"Comprobante no tiene atributo '{name}'"
        return col

    # ==================== CONSULTAS BÁSICAS ====================

    async def obtener_por_numero(
        self, 
        numero_comprobante: str
    ) -> Optional[Comprobante]:
        """Busca comprobante por número único."""
        numero_col = self._get_column('numero')
        
        stmt = select(Comprobante).where(numero_col == numero_comprobante)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def listar_por_tipo(
        self,
        tipo: str,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Comprobante]:
        """
        Lista comprobantes por tipo con filtros opcionales de fecha.
        
        Args:
            tipo: Tipo de comprobante ('factura', 'recibo', 'nota_credito', etc.)
            fecha_desde: Fecha inicial (opcional)
            fecha_hasta: Fecha final (opcional)
        """
        tipo_col = self._get_column('tipo')
        fecha_emision_col = self._get_column('fecha_emision')
        
        stmt = select(Comprobante).where(tipo_col == tipo)
        
        if fecha_desde:
            stmt = stmt.where(fecha_emision_col >= fecha_desde)
        if fecha_hasta:
            stmt = stmt.where(fecha_emision_col <= fecha_hasta)
        
        stmt = stmt.order_by(fecha_emision_col.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def listar_por_pago(self, pago_id: int) -> List[Comprobante]:
        """Lista todos los comprobantes asociados a un pago."""
        pago_id_col = self._get_column('pago_id')
        
        stmt = select(Comprobante).where(pago_id_col == pago_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== VALIDACIONES ====================

    async def verificar_numero_duplicado(
        self,
        numero: str,
        excluir_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si existe un comprobante con el mismo número.
        
        Args:
            numero: Número de comprobante a verificar
            excluir_id: ID a excluir en la búsqueda (para updates)
            
        Returns:
            True si existe duplicado, False si no
        """
        numero_col = self._get_column('numero')
        id_col = self._get_column('id')
        
        stmt = select(Comprobante).where(numero_col == numero)
        
        if excluir_id:
            stmt = stmt.where(id_col != excluir_id)
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    # ==================== BÚSQUEDA AVANZADA ====================

    async def buscar_comprobantes(
        self,
        numero: Optional[str] = None,
        tipo: Optional[str] = None,
        pago_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limit: int = 50
    ) -> List[Comprobante]:
        """
        Búsqueda flexible de comprobantes con múltiples filtros.
        
        Args:
            numero: Número exacto o parcial
            tipo: Tipo de comprobante
            pago_id: ID de pago asociado
            fecha_desde: Fecha inicial
            fecha_hasta: Fecha final
            limit: Límite de resultados
        """
        # ✅ Obtener columnas con assert
        numero_col = self._get_column('numero')
        tipo_col = self._get_column('tipo')
        pago_id_col = self._get_column('pago_id')
        fecha_emision_col = self._get_column('fecha_emision')
        
        stmt = select(Comprobante)
        
        filtros = []
        
        if numero:
            filtros.append(numero_col.ilike(f"%{numero}%"))
        if tipo:
            filtros.append(tipo_col == tipo)
        if pago_id:
            filtros.append(pago_id_col == pago_id)
        if fecha_desde:
            filtros.append(fecha_emision_col >= fecha_desde)
        if fecha_hasta:
            filtros.append(fecha_emision_col <= fecha_hasta)
        
        if filtros:
            stmt = stmt.where(and_(*filtros))
        
        stmt = stmt.order_by(fecha_emision_col.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== MÉTODOS AUXILIARES ====================

    async def contar_por_tipo(self, tipo: str) -> int:
        """Cuenta comprobantes de un tipo específico."""
        from sqlalchemy import func
        
        tipo_col = self._get_column('tipo')
        id_col = self._get_column('id')
        
        stmt = select(func.count(id_col)).where(tipo_col == tipo)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def listar_tipos_disponibles(self) -> List[str]:
        """
        Obtiene lista de tipos de comprobantes únicos en el sistema.
        
        Returns:
            Lista de tipos de comprobante
        """
        from sqlalchemy import distinct
        
        tipo_col = self._get_column('tipo')
        
        stmt = select(distinct(tipo_col)).order_by(tipo_col.asc())
        result = await self.session.execute(stmt)
        
        return [row[0] for row in result.all() if row[0]]

    async def obtener_ultimo_numero(self, tipo: str) -> Optional[str]:
        """
        Obtiene el último número de comprobante de un tipo.
        Útil para generar números correlativos.
        
        Args:
            tipo: Tipo de comprobante
            
        Returns:
            Último número o None si no existe
        """
        tipo_col = self._get_column('tipo')
        numero_col = self._get_column('numero')
        fecha_emision_col = self._get_column('fecha_emision')
        
        stmt = (
            select(Comprobante)
            .where(tipo_col == tipo)
            .order_by(fecha_emision_col.desc(), numero_col.desc())
            .limit(1)
        )
        
        result = await self.session.execute(stmt)
        comprobante = result.scalar_one_or_none()
        
        if comprobante:
            return getattr(comprobante, 'numero', None)
        return None

    async def listar_sin_pago_asociado(
        self,
        tipo: Optional[str] = None,
        limit: int = 50
    ) -> List[Comprobante]:
        """
        Lista comprobantes que no tienen pago asociado.
        Útil para detectar inconsistencias.
        
        Args:
            tipo: Filtrar por tipo (opcional)
            limit: Límite de resultados
            
        Returns:
            Lista de comprobantes sin pago
        """
        pago_id_col = self._get_column('pago_id')
        fecha_emision_col = self._get_column('fecha_emision')
        
        stmt = select(Comprobante).where(pago_id_col.is_(None))
        
        if tipo:
            tipo_col = self._get_column('tipo')
            stmt = stmt.where(tipo_col == tipo)
        
        stmt = stmt.order_by(fecha_emision_col.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def actualizar_comprobante(
        self,
        comprobante_id: int,
        numero: Optional[str] = None,
        tipo: Optional[str] = None,
        fecha_emision: Optional[date] = None
    ) -> Optional[Comprobante]:
        """
        Actualiza datos de un comprobante.
        
        Args:
            comprobante_id: ID del comprobante
            numero: Nuevo número (opcional)
            tipo: Nuevo tipo (opcional)
            fecha_emision: Nueva fecha (opcional)
            
        Returns:
            Comprobante actualizado o None si no existe
        """
        comprobante = await self.get(comprobante_id)
        
        if not comprobante:
            return None
        
        # ✅ Actualizar con setattr y assert
        if numero is not None:
            assert hasattr(comprobante, 'numero'), "Comprobante debe tener 'numero'"
            setattr(comprobante, 'numero', numero)
        
        if tipo is not None:
            assert hasattr(comprobante, 'tipo'), "Comprobante debe tener 'tipo'"
            setattr(comprobante, 'tipo', tipo)
        
        if fecha_emision is not None:
            assert hasattr(comprobante, 'fecha_emision'), "Comprobante debe tener 'fecha_emision'"
            setattr(comprobante, 'fecha_emision', fecha_emision)
        
        await self.session.commit()
        await self.session.refresh(comprobante)
        
        return comprobante

    async def eliminar_comprobante(self, comprobante_id: int) -> bool:
        """
        Elimina un comprobante del sistema.
        
        Args:
            comprobante_id: ID del comprobante a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        comprobante = await self.get(comprobante_id)
        
        if not comprobante:
            return False
        
        await self.session.delete(comprobante)
        await self.session.commit()
        
        return True
