# app/infrastructure/db/repositories/finanzas/estado_cuenta_nino_repo.py
from typing import Optional, List, Dict, Tuple, Any
from datetime import date
from decimal import Decimal
from sqlalchemy import select, case, func, and_, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import EstadoCuentaNino
from app.infrastructure.db.models.alumnos import Alumno


class EstadoCuentaNinoRepository(BaseRepository[EstadoCuentaNino]):
    """
    Repositorio para estados de cuenta de alumnos.
    Gestiona saldos pendientes, deudas y estado financiero individual.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, EstadoCuentaNino)

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
        col = getattr(EstadoCuentaNino, name, None)
        assert col is not None, f"EstadoCuentaNino no tiene atributo '{name}'"
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
        rel = getattr(EstadoCuentaNino, name, None)
        assert rel is not None, f"EstadoCuentaNino no tiene relación '{name}'"
        return rel

    # ==================== CONSULTAS BÁSICAS ====================

    async def obtener_por_alumno(self, alumno_id: int) -> Optional[EstadoCuentaNino]:
        """Obtiene el estado de cuenta actual de un alumno."""
        alumno_id_col = self._get_column('alumno_id')
        
        stmt = select(EstadoCuentaNino).where(alumno_id_col == alumno_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def obtener_con_relaciones(self, estado_id: int) -> Optional[EstadoCuentaNino]:
        """Obtiene estado de cuenta con alumno y sede cargados."""
        id_col = self._get_column('id')
        
        # ✅ Obtener relaciones con helper
        alumno_rel = self._get_relationship('alumno')
        sede_rel = self._get_relationship('sede')
        
        stmt = (
            select(EstadoCuentaNino)
            .options(
                selectinload(alumno_rel),
                selectinload(sede_rel)
            )
            .where(id_col == estado_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def listar_por_sede(
        self,
        sede_id: int,
        solo_con_deuda: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[EstadoCuentaNino]:
        """
        Lista estados de cuenta de una sede.
        
        Args:
            sede_id: ID de la sede
            solo_con_deuda: Si True, filtra solo alumnos con saldo pendiente > 0
        """
        sede_id_col = self._get_column('sede_id')
        saldo_pendiente_col = self._get_column('saldo_pendiente')
        
        stmt = select(EstadoCuentaNino).where(sede_id_col == sede_id)
        
        if solo_con_deuda:
            stmt = stmt.where(saldo_pendiente_col > 0)
        
        stmt = stmt.order_by(saldo_pendiente_col.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== ACTUALIZACIÓN DE SALDOS ====================

    async def actualizar_saldo(
        self,
        alumno_id: int,
        total_debe: Decimal,
        total_pagado: Decimal,
        ultima_actualizacion: Optional[date] = None
    ) -> EstadoCuentaNino:
        """
        Actualiza el estado de cuenta de un alumno (crea si no existe).
        
        Args:
            alumno_id: ID del alumno
            total_debe: Total que debe pagar
            total_pagado: Total que ya pagó
            ultima_actualizacion: Fecha de actualización (default: hoy)
            
        Returns:
            Estado de cuenta actualizado
        """
        # ✅ Obtener sede del alumno con getattr
        alumno_id_col_alumno = getattr(Alumno, 'id', None)
        assert alumno_id_col_alumno is not None, "Alumno debe tener 'id'"
        
        sede_id_col_alumno = getattr(Alumno, 'sede_id', None)
        assert sede_id_col_alumno is not None, "Alumno debe tener 'sede_id'"
        
        stmt = select(sede_id_col_alumno).where(alumno_id_col_alumno == alumno_id)
        result = await self.session.execute(stmt)
        sede_id: Optional[int] = result.scalar_one_or_none()
        
        if not sede_id:
            raise ValueError(f"Alumno {alumno_id} no encontrado")
        
        # Buscar estado existente
        estado = await self.obtener_por_alumno(alumno_id)
        
        saldo_pendiente: Decimal = total_debe - total_pagado
        fecha_actualizacion: date = ultima_actualizacion or date.today()
        
        if estado:
            # ✅ Actualizar existente con setattr
            assert hasattr(estado, 'total_debe'), "EstadoCuentaNino debe tener 'total_debe'"
            setattr(estado, 'total_debe', total_debe)
            
            assert hasattr(estado, 'total_pagado'), "EstadoCuentaNino debe tener 'total_pagado'"
            setattr(estado, 'total_pagado', total_pagado)
            
            assert hasattr(estado, 'saldo_pendiente'), "EstadoCuentaNino debe tener 'saldo_pendiente'"
            setattr(estado, 'saldo_pendiente', saldo_pendiente)
            
            assert hasattr(estado, 'ultima_actualizacion'), "EstadoCuentaNino debe tener 'ultima_actualizacion'"
            setattr(estado, 'ultima_actualizacion', fecha_actualizacion)
        else:
            # Crear nuevo
            estado = EstadoCuentaNino(
                alumno_id=alumno_id,
                sede_id=sede_id,
                total_debe=total_debe,
                total_pagado=total_pagado,
                saldo_pendiente=saldo_pendiente,
                ultima_actualizacion=fecha_actualizacion
            )
            self.session.add(estado)
        
        await self.session.commit()
        await self.session.refresh(estado)
        
        return estado

    async def registrar_pago(
        self,
        alumno_id: int,
        monto_pago: Decimal
    ) -> Optional[EstadoCuentaNino]:
        """
        Registra un pago y actualiza el saldo pendiente.
        
        Args:
            alumno_id: ID del alumno
            monto_pago: Monto pagado
            
        Returns:
            Estado de cuenta actualizado o None si no existe
        """
        estado = await self.obtener_por_alumno(alumno_id)
        
        if not estado:
            return None
        
        # ✅ Acceso seguro con getattr
        total_pagado_actual: Decimal = getattr(estado, 'total_pagado', Decimal('0.00'))
        total_debe_actual: Decimal = getattr(estado, 'total_debe', Decimal('0.00'))
        
        nuevo_total_pagado: Decimal = total_pagado_actual + monto_pago
        nuevo_saldo_pendiente: Decimal = total_debe_actual - nuevo_total_pagado
        
        # ✅ Actualizar con setattr
        assert hasattr(estado, 'total_pagado'), "EstadoCuentaNino debe tener 'total_pagado'"
        setattr(estado, 'total_pagado', nuevo_total_pagado)
        
        assert hasattr(estado, 'saldo_pendiente'), "EstadoCuentaNino debe tener 'saldo_pendiente'"
        setattr(estado, 'saldo_pendiente', nuevo_saldo_pendiente)
        
        assert hasattr(estado, 'ultima_actualizacion'), "EstadoCuentaNino debe tener 'ultima_actualizacion'"
        setattr(estado, 'ultima_actualizacion', date.today())
        
        await self.session.commit()
        await self.session.refresh(estado)
        
        return estado

    async def registrar_cargo(
        self,
        alumno_id: int,
        monto_cargo: Decimal
    ) -> Optional[EstadoCuentaNino]:
        """
        Registra un nuevo cargo (aumenta deuda).
        
        Args:
            alumno_id: ID del alumno
            monto_cargo: Monto del cargo
            
        Returns:
            Estado de cuenta actualizado o None si no existe
        """
        estado = await self.obtener_por_alumno(alumno_id)
        
        if not estado:
            return None
        
        # ✅ Acceso seguro con getattr
        total_debe_actual: Decimal = getattr(estado, 'total_debe', Decimal('0.00'))
        total_pagado_actual: Decimal = getattr(estado, 'total_pagado', Decimal('0.00'))
        
        nuevo_total_debe: Decimal = total_debe_actual + monto_cargo
        nuevo_saldo_pendiente: Decimal = nuevo_total_debe - total_pagado_actual
        
        # ✅ Actualizar con setattr
        assert hasattr(estado, 'total_debe'), "EstadoCuentaNino debe tener 'total_debe'"
        setattr(estado, 'total_debe', nuevo_total_debe)
        
        assert hasattr(estado, 'saldo_pendiente'), "EstadoCuentaNino debe tener 'saldo_pendiente'"
        setattr(estado, 'saldo_pendiente', nuevo_saldo_pendiente)
        
        assert hasattr(estado, 'ultima_actualizacion'), "EstadoCuentaNino debe tener 'ultima_actualizacion'"
        setattr(estado, 'ultima_actualizacion', date.today())
        
        await self.session.commit()
        await self.session.refresh(estado)
        
        return estado

    # ==================== ESTADÍSTICAS Y REPORTES ====================

    async def obtener_resumen_sede(self, sede_id: int) -> Dict[str, Any]:
        """
        Resumen financiero de todos los alumnos de una sede.
        
        Returns:
            dict con {total_alumnos, total_debe, total_pagado, saldo_pendiente_total}
        """
        id_col = self._get_column('id')
        sede_id_col = self._get_column('sede_id')
        total_debe_col = self._get_column('total_debe')
        total_pagado_col = self._get_column('total_pagado')
        saldo_pendiente_col = self._get_column('saldo_pendiente')
        
        stmt = (
            select(
                func.count(id_col),
                func.sum(total_debe_col),
                func.sum(total_pagado_col),
                func.sum(saldo_pendiente_col),
                func.count(case((saldo_pendiente_col > 0, 1)))
            )
            .where(sede_id_col == sede_id)
        )
        
        result = await self.session.execute(stmt)
        row: Row[Tuple[int, Optional[Decimal], Optional[Decimal], Optional[Decimal], int]] = result.one()
        
        total_alumnos: int = row[0]
        total_debe: Optional[Decimal] = row[1]
        total_pagado: Optional[Decimal] = row[2]
        saldo_pendiente: Optional[Decimal] = row[3]
        alumnos_con_deuda: int = row[4]
        
        total_debe_float: float = float(total_debe) if total_debe else 0.0
        total_pagado_float: float = float(total_pagado) if total_pagado else 0.0
        
        return {
            'sede_id': sede_id,
            'total_alumnos': total_alumnos,
            'total_debe': total_debe_float,
            'total_pagado': total_pagado_float,
            'saldo_pendiente_total': float(saldo_pendiente) if saldo_pendiente else 0.0,
            'alumnos_con_deuda': alumnos_con_deuda,
            'tasa_pago': round((total_pagado_float / total_debe_float * 100) if total_debe_float > 0 else 0, 2)
        }

    async def listar_deudores_mayores(
        self,
        sede_id: int,
        monto_minimo: Decimal = Decimal('100.00'),
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Lista alumnos con mayor deuda.
        
        Args:
            sede_id: ID de la sede
            monto_minimo: Deuda mínima para incluir
            limit: Cantidad de resultados
            
        Returns:
            Lista de dicts con información de deudores
        """
        sede_id_col = self._get_column('sede_id')
        saldo_pendiente_col = self._get_column('saldo_pendiente')
        
        # ✅ Obtener relación alumno
        alumno_rel = self._get_relationship('alumno')
        
        stmt = (
            select(EstadoCuentaNino)
            .options(selectinload(alumno_rel))
            .where(
                and_(
                    sede_id_col == sede_id,
                    saldo_pendiente_col >= monto_minimo
                )
            )
            .order_by(saldo_pendiente_col.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        estados: List[EstadoCuentaNino] = list(result.scalars().all())
        
        resultado: List[Dict[str, Any]] = []
        for estado in estados:
            # ✅ Acceso seguro a atributos
            alumno_id_val: int = getattr(estado, 'alumno_id', 0)
            total_debe_val: Decimal = getattr(estado, 'total_debe', Decimal('0.00'))
            total_pagado_val: Decimal = getattr(estado, 'total_pagado', Decimal('0.00'))
            saldo_pendiente_val: Decimal = getattr(estado, 'saldo_pendiente', Decimal('0.00'))
            ultima_act_val: Optional[date] = getattr(estado, 'ultima_actualizacion', None)
            
            # ✅ Acceso seguro a relación alumno
            alumno = getattr(estado, 'alumno', None)
            if alumno:
                nombres: str = getattr(alumno, 'nombres', '')
                apellidos: str = getattr(alumno, 'apellidos', '')
                alumno_nombre = f"{nombres} {apellidos}"
            else:
                alumno_nombre = "N/A"
            
            porcentaje_pagado: float = round(
                (float(total_pagado_val) / float(total_debe_val) * 100) if total_debe_val > 0 else 0, 
                2
            )
            
            resultado.append({
                'alumno_id': alumno_id_val,
                'alumno_nombre': alumno_nombre,
                'total_debe': float(total_debe_val),
                'total_pagado': float(total_pagado_val),
                'saldo_pendiente': float(saldo_pendiente_val),
                'porcentaje_pagado': porcentaje_pagado,
                'ultima_actualizacion': ultima_act_val.isoformat() if ultima_act_val else None
            })
        
        return resultado

    async def listar_al_dia(
        self,
        sede_id: int,
        limit: int = 100
    ) -> List[EstadoCuentaNino]:
        """Lista alumnos sin deuda (saldo pendiente = 0)."""
        sede_id_col = self._get_column('sede_id')
        saldo_pendiente_col = self._get_column('saldo_pendiente')
        
        stmt = (
            select(EstadoCuentaNino)
            .where(
                and_(
                    sede_id_col == sede_id,
                    saldo_pendiente_col == 0
                )
            )
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== VALIDACIONES ====================

    async def verificar_alumno_al_dia(self, alumno_id: int) -> bool:
        """
        Verifica si un alumno está al día (sin deuda).
        
        Returns:
            True si no tiene deuda, False si tiene deuda o no existe estado
        """
        estado = await self.obtener_por_alumno(alumno_id)
        
        if not estado:
            return False
        
        # ✅ Acceso seguro
        saldo_pendiente_val: Decimal = getattr(estado, 'saldo_pendiente', Decimal('0.00'))
        
        return saldo_pendiente_val <= Decimal('0.00')

    async def obtener_porcentaje_morosidad(self, sede_id: int) -> Decimal:
        """
        Calcula el porcentaje de alumnos con deuda en una sede.
        
        Returns:
            Porcentaje de morosidad (0-100)
        """
        id_col = self._get_column('id')
        sede_id_col = self._get_column('sede_id')
        saldo_pendiente_col = self._get_column('saldo_pendiente')
        
        stmt = (
            select(
                func.count(id_col),
                func.count(case((saldo_pendiente_col > 0, 1)))
            )
            .where(sede_id_col == sede_id)
        )
        
        result = await self.session.execute(stmt)
        row: Row[Tuple[int, int]] = result.one()
        
        total: int = row[0]
        con_deuda: int = row[1]
        
        if not total or total == 0:
            return Decimal('0.00')
        
        porcentaje: Decimal = (Decimal(str(con_deuda)) / Decimal(str(total))) * Decimal('100')
        
        return round(porcentaje, 2)
