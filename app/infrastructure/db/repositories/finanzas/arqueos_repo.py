# app/infrastructure/db/repositories/finanzas/arqueos_repo.py
from typing import Optional, List, Dict, Tuple, cast
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select, func, and_, extract, case, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models.finanzas import Arqueo


class ArqueosRepository(BaseRepository[Arqueo]):
    """
    Repositorio para arqueos de caja mensuales.
    Gestiona resúmenes financieros consolidados por mes.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Arqueo)

    # ==================== CONSULTAS BÁSICAS ====================

    async def obtener_por_mes_anio(
        self, 
        sede_id: int, 
        mes: int, 
        anio: int
    ) -> Optional[Arqueo]:
        """
        Obtiene el arqueo de un mes específico.
        
        Args:
            sede_id: ID de la sede
            mes: Mes (1-12)
            anio: Año (ej: 2025)
        """
        stmt = select(Arqueo).where(
            and_(
                Arqueo.sede_id == sede_id,
                Arqueo.mes == mes,
                Arqueo.anio == anio
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def listar_por_sede_anio(
        self,
        sede_id: int,
        anio: int,
        order_by_desc: bool = False
    ) -> List[Arqueo]:
        """Lista todos los arqueos de una sede en un año."""
        stmt = select(Arqueo).where(
            and_(
                Arqueo.sede_id == sede_id,
                Arqueo.anio == anio
            )
        )
        
        if order_by_desc:
            stmt = stmt.order_by(Arqueo.mes.desc())
        else:
            stmt = stmt.order_by(Arqueo.mes.asc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obtener_con_relaciones(self, arqueo_id: int) -> Optional[Arqueo]:
        """Obtiene arqueo con sede y usuario elaborador."""
        stmt = (
            select(Arqueo)
            .options(
                selectinload(Arqueo.sede),
                selectinload(Arqueo.elaborador)
            )
            .where(Arqueo.id == arqueo_id)
        )
        result = await self.session.execute(stmt)
        arqueo = result.scalar_one_or_none()
        return cast(Optional[Arqueo], arqueo)

    # ==================== CREACIÓN Y ACTUALIZACIÓN ====================

    async def crear_arqueo_mensual(
        self,
        sede_id: int,
        mes: int,
        anio: int,
        saldo_inicial: Decimal,
        total_ingresos: Decimal,
        total_egresos: Decimal,
        elaborado_por_id: int,
        observaciones: Optional[str] = None
    ) -> Arqueo:
        """
        Crea un nuevo arqueo mensual.
        
        Args:
            sede_id: ID de la sede
            mes: Mes (1-12)
            anio: Año
            saldo_inicial: Saldo al inicio del mes
            total_ingresos: Total de ingresos del mes
            total_egresos: Total de egresos del mes
            elaborado_por_id: ID del usuario que elabora
            observaciones: Notas opcionales
            
        Returns:
            Arqueo creado
            
        Raises:
            ValueError: Si ya existe un arqueo para ese mes/año
        """
        # Verificar si ya existe
        existe = await self.obtener_por_mes_anio(sede_id, mes, anio)
        if existe:
            raise ValueError(f"Ya existe un arqueo para {mes}/{anio} en sede {sede_id}")
        
        # Calcular saldo final
        saldo_final: Decimal = saldo_inicial + total_ingresos - total_egresos
        
        # Crear arqueo
        arqueo = Arqueo(
            sede_id=sede_id,
            mes=mes,
            anio=anio,
            saldo_inicial=saldo_inicial,
            total_ingresos=total_ingresos,
            total_egresos=total_egresos,
            saldo_final=saldo_final,
            observaciones=observaciones,
            elaborado_por=elaborado_por_id
        )
        
        self.session.add(arqueo)
        await self.session.commit()
        await self.session.refresh(arqueo)
        
        return arqueo

    async def actualizar_arqueo(
        self,
        arqueo_id: int,
        saldo_inicial: Optional[Decimal] = None,
        total_ingresos: Optional[Decimal] = None,
        total_egresos: Optional[Decimal] = None,
        observaciones: Optional[str] = None,
        pdf_url: Optional[str] = None
    ) -> Optional[Arqueo]:
        """
        Actualiza un arqueo existente y recalcula saldo final.
        
        Args:
            arqueo_id: ID del arqueo
            saldo_inicial: Nuevo saldo inicial (opcional)
            total_ingresos: Nuevos ingresos (opcional)
            total_egresos: Nuevos egresos (opcional)
            observaciones: Nuevas observaciones (opcional)
            pdf_url: URL del PDF generado (opcional)
            
        Returns:
            Arqueo actualizado o None si no existe
        """
        arqueo = cast(Optional[Arqueo], await self.get(arqueo_id))
        
        if not arqueo:
            return None
        
        # Actualizar campos si se proporcionan
        if saldo_inicial is not None:
            arqueo.saldo_inicial = saldo_inicial
        if total_ingresos is not None:
            arqueo.total_ingresos = total_ingresos
        if total_egresos is not None:
            arqueo.total_egresos = total_egresos
        if observaciones is not None:
            arqueo.observaciones = observaciones
        if pdf_url is not None:
            arqueo.pdf_url = pdf_url
        
        # Recalcular saldo final con tipos explícitos
        saldo_inicial_actual: Decimal = arqueo.saldo_inicial
        total_ingresos_actual: Decimal = arqueo.total_ingresos
        total_egresos_actual: Decimal = arqueo.total_egresos
        arqueo.saldo_final = saldo_inicial_actual + total_ingresos_actual - total_egresos_actual
        
        await self.session.commit()
        await self.session.refresh(arqueo)
        
        return arqueo

    # ==================== ESTADÍSTICAS Y REPORTES ====================

    async def obtener_resumen_anual(self, sede_id: int, anio: int) -> Dict[str, any]:
        """
        Resumen financiero anual consolidado.
        
        Returns:
            dict con {total_ingresos, total_egresos, saldo_inicial, saldo_final, meses_con_arqueo}
        """
        stmt = (
            select(
                func.sum(Arqueo.total_ingresos).label('total_ingresos'),
                func.sum(Arqueo.total_egresos).label('total_egresos'),
                func.count(Arqueo.id).label('meses_con_arqueo')
            )
            .where(
                and_(
                    Arqueo.sede_id == sede_id,
                    Arqueo.anio == anio
                )
            )
        )
        
        result = await self.session.execute(stmt)
        row: Row[Tuple[Optional[Decimal], Optional[Decimal], int]] = result.one()
        
        # Obtener saldo inicial del primer mes
        primer_arqueo = await self.obtener_por_mes_anio(sede_id, 1, anio)
        saldo_inicial: float = float(primer_arqueo.saldo_inicial) if primer_arqueo else 0.0
        
        # Obtener saldo final del último mes con arqueo
        arqueos_anio: List[Arqueo] = await self.listar_por_sede_anio(sede_id, anio, order_by_desc=True)
        saldo_final: float = float(arqueos_anio[0].saldo_final) if arqueos_anio else 0.0
        
        # Extraer valores tipados
        total_ingresos_value: Optional[Decimal] = row[0]
        total_egresos_value: Optional[Decimal] = row[1]
        meses_con_arqueo_value: int = row[2]
        
        total_ingresos_float: float = float(total_ingresos_value) if total_ingresos_value else 0.0
        total_egresos_float: float = float(total_egresos_value) if total_egresos_value else 0.0
        
        return {
            'sede_id': sede_id,
            'anio': anio,
            'total_ingresos': total_ingresos_float,
            'total_egresos': total_egresos_float,
            'saldo_inicial': saldo_inicial,
            'saldo_final': saldo_final,
            'balance_anual': total_ingresos_float - total_egresos_float,
            'meses_con_arqueo': meses_con_arqueo_value
        }

    async def obtener_comparativo_meses(
        self,
        sede_id: int,
        anio: int
    ) -> List[Dict[str, any]]:
        """
        Comparativo mes a mes para gráficas.
        
        Returns:
            Lista de dicts con {mes, ingresos, egresos, balance, saldo_final}
        """
        arqueos: List[Arqueo] = await self.listar_por_sede_anio(sede_id, anio, order_by_desc=False)
        
        resultado: List[Dict[str, any]] = []
        for arqueo in arqueos:
            ingresos: Decimal = arqueo.total_ingresos
            egresos: Decimal = arqueo.total_egresos
            balance: Decimal = ingresos - egresos
            saldo: Decimal = arqueo.saldo_final
            
            resultado.append({
                'mes': arqueo.mes,
                'nombre_mes': self._obtener_nombre_mes(arqueo.mes),
                'ingresos': float(ingresos),
                'egresos': float(egresos),
                'balance': float(balance),
                'saldo_final': float(saldo)
            })
        
        return resultado

    async def verificar_arqueo_pendiente(
        self,
        sede_id: int,
        mes: int,
        anio: int
    ) -> bool:
        """
        Verifica si falta generar el arqueo de un mes.
        
        Returns:
            True si NO existe arqueo (está pendiente), False si ya existe
        """
        arqueo = await self.obtener_por_mes_anio(sede_id, mes, anio)
        return arqueo is None

    async def listar_arqueos_pendientes(
        self,
        sede_id: int,
        hasta_mes: int,
        hasta_anio: int
    ) -> List[Dict[str, any]]:
        """
        Lista meses sin arqueo hasta una fecha.
        
        Args:
            sede_id: ID de la sede
            hasta_mes: Mes límite
            hasta_anio: Año límite
            
        Returns:
            Lista de dicts con {mes, anio} de meses pendientes
        """
        # Obtener todos los arqueos de la sede hasta la fecha
        stmt = (
            select(Arqueo.mes, Arqueo.anio)
            .where(Arqueo.sede_id == sede_id)
            .order_by(Arqueo.anio, Arqueo.mes)
        )
        
        result = await self.session.execute(stmt)
        rows: List[Row[Tuple[int, int]]] = list(result.all())
        
        # Crear set con tipos explícitos
        arqueos_existentes: set[Tuple[int, int]] = {
            (cast(int, row[0]), cast(int, row[1])) for row in rows
        }
        
        # Generar lista de todos los meses hasta la fecha límite
        meses_esperados: List[Dict[str, any]] = []
        for mes in range(1, hasta_mes + 1):
            if (mes, hasta_anio) not in arqueos_existentes:
                meses_esperados.append({
                    'mes': mes,
                    'anio': hasta_anio,
                    'nombre_mes': self._obtener_nombre_mes(mes)
                })
        
        return meses_esperados

    async def obtener_datos_arqueo(
        self,
        sede_id: int,
        mes: int,
        año: int
    ) -> Dict[str, any]:
        """
        Obtiene todos los datos necesarios para generar un arqueo mensual.
        
        Returns:
            dict con {saldo_inicial, total_ingresos, total_egresos, saldo_final, movimientos}
        """
        from calendar import monthrange
        
        # Rango de fechas del mes
        primer_dia = date(año, mes, 1)
        ultimo_dia = date(año, mes, monthrange(año, mes)[1])
        
        # Saldo inicial (saldo al último día del mes anterior)
        saldo_inicial: Decimal
        if mes == 1:
            saldo_inicial = Decimal('0.00')
        else:
            ultimo_dia_mes_anterior = date(año, mes - 1, monthrange(año, mes - 1)[1])
            saldo_inicial = await self.calcular_saldo_acumulado(sede_id, ultimo_dia_mes_anterior)
        
        # Movimientos del mes
        movimientos_mes = await self.listar_por_sede_fecha(sede_id, primer_dia, ultimo_dia)
        
        # Totales del mes
        totales = await self.calcular_saldo_periodo(sede_id, primer_dia, ultimo_dia)
        
        total_ingresos: Decimal = totales['total_ingresos']
        total_egresos: Decimal = totales['total_egresos']
        saldo_final: Decimal = saldo_inicial + totales['saldo_neto']
        
        return {
            'saldo_inicial': float(saldo_inicial),
            'total_ingresos': float(total_ingresos),
            'total_egresos': float(total_egresos),
            'saldo_final': float(saldo_final),
            'cantidad_movimientos': len(movimientos_mes),
            'movimientos': movimientos_mes
        }

    async def calcular_saldo_periodo(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date
    ) -> Dict[str, Decimal]:
        """
        Calcula saldo del periodo (ingresos - egresos).
        
        Returns:
            dict con {total_ingresos, total_egresos, saldo_neto}
        """
        from app.infrastructure.db.models.finanzas import LibroCaja, TipoMovimientoEnum
        
        stmt = (
            select(
                func.sum(
                    case(
                        (LibroCaja.tipo == TipoMovimientoEnum.INGRESO, LibroCaja.monto),
                        else_=0
                    )
                ).label('total_ingresos'),
                func.sum(
                    case(
                        (LibroCaja.tipo == TipoMovimientoEnum.EGRESO, LibroCaja.monto),
                        else_=0
                    )
                ).label('total_egresos')
            )
            .where(
                and_(
                    LibroCaja.sede_id == sede_id,
                    LibroCaja.fecha >= fecha_desde,
                    LibroCaja.fecha <= fecha_hasta
                )
            )
        )
        
        result = await self.session.execute(stmt)
        row: Row[Tuple[Optional[Decimal], Optional[Decimal]]] = result.one()
        
        total_ingresos: Decimal = row[0] if row[0] else Decimal('0.00')
        total_egresos: Decimal = row[1] if row[1] else Decimal('0.00')
        
        return {
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'saldo_neto': total_ingresos - total_egresos
        }

    async def calcular_saldo_acumulado(
        self,
        sede_id: int,
        hasta_fecha: date
    ) -> Decimal:
        """Calcula saldo acumulado desde el inicio hasta una fecha."""
        from app.infrastructure.db.models.finanzas import LibroCaja, TipoMovimientoEnum
        
        stmt = (
            select(
                func.sum(
                    case(
                        (LibroCaja.tipo == TipoMovimientoEnum.INGRESO, LibroCaja.monto),
                        (LibroCaja.tipo == TipoMovimientoEnum.EGRESO, -LibroCaja.monto),
                        else_=0
                    )
                )
            )
            .where(
                and_(
                    LibroCaja.sede_id == sede_id,
                    LibroCaja.fecha <= hasta_fecha
                )
            )
        )
        
        result = await self.session.execute(stmt)
        saldo: Optional[Decimal] = result.scalar_one_or_none()
        
        return saldo if saldo else Decimal('0.00')

    async def listar_por_sede_fecha(
        self,
        sede_id: int,
        fecha_desde: date,
        fecha_hasta: date
    ) -> List[any]:
        """Lista movimientos de caja por sede y rango de fechas."""
        from app.infrastructure.db.models.finanzas import LibroCaja
        
        stmt = (
            select(LibroCaja)
            .where(
                and_(
                    LibroCaja.sede_id == sede_id,
                    LibroCaja.fecha >= fecha_desde,
                    LibroCaja.fecha <= fecha_hasta
                )
            )
            .order_by(LibroCaja.fecha.asc(), LibroCaja.creado_en.asc())
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ==================== UTILIDADES ====================

    @staticmethod
    def _obtener_nombre_mes(mes: int) -> str:
        """Convierte número de mes a nombre."""
        meses: List[str] = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        return meses[mes - 1] if 1 <= mes <= 12 else f"Mes {mes}"
