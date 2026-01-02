#app/kernel/application/finanzas/estado_cuenta/obtener_estado_cuenta_detallado.py
from decimal import Decimal
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort
from app.kernel.domain.finanzas.ports import (
    IEstadoCuentaNinoRepository,
    IPagoRepository,
    IComprobanteRepository,
    ICalculadorDescuento,
    IPlanCuotaRepository,
)
from app.kernel.domain.alumnos.errors import AlumnoNoEncontradoError
from app.kernel.domain.finanzas.errors import EstadoCuentaNoEncontradoError


class EstadoCuentaDetalladoDTO:
    """DTO de respuesta para estado de cuenta detallado"""
    
    def __init__(
        self,
        alumno_id: int,
        alumno_nombre_completo: str,
        fecha_consulta: datetime,
        deuda_total: Decimal,
        total_pagado: Decimal,
        saldo_pendiente: Decimal,
        descuentos_aplicados: Decimal,
        cuotas: List["CuotaDetalleDTO"],
        pagos_realizados: List["PagoDetalleDTO"],
        comprobantes: List["ComprobanteDetalleDTO"],
    ) -> None:
        self.alumno_id = alumno_id
        self.alumno_nombre_completo = alumno_nombre_completo
        self.fecha_consulta = fecha_consulta
        self.deuda_total = deuda_total
        self.total_pagado = total_pagado
        self.saldo_pendiente = saldo_pendiente
        self.descuentos_aplicados = descuentos_aplicados
        self.cuotas = cuotas
        self.pagos_realizados = pagos_realizados
        self.comprobantes = comprobantes


class CuotaDetalleDTO:
    """DTO para detalle de cuota"""
    
    def __init__(
        self,
        cuota_id: int,
        numero_cuota: int,
        monto: Decimal,
        fecha_vencimiento: date,
        estado: str,
        monto_pagado: Decimal,
        dias_mora: int,
    ) -> None:
        self.cuota_id = cuota_id
        self.numero_cuota = numero_cuota
        self.monto = monto
        self.fecha_vencimiento = fecha_vencimiento
        self.estado = estado
        self.monto_pagado = monto_pagado
        self.dias_mora = dias_mora


class PagoDetalleDTO:
    """DTO para detalle de pago"""
    
    def __init__(
        self,
        pago_id: int,
        fecha_pago: datetime,
        monto: Decimal,
        metodo_pago: str,
        categoria_nombre: str,
        nro_recibo: Optional[str],
        observaciones: Optional[str],
    ) -> None:
        self.pago_id = pago_id
        self.fecha_pago = fecha_pago
        self.monto = monto
        self.metodo_pago = metodo_pago
        self.categoria_nombre = categoria_nombre
        self.nro_recibo = nro_recibo
        self.observaciones = observaciones


class ComprobanteDetalleDTO:
    """DTO para detalle de comprobante"""
    
    def __init__(
        self,
        comprobante_id: int,
        tipo_comprobante: str,
        numero_comprobante: str,
        fecha_emision: datetime,
        monto_total: Decimal,
        url_archivo: Optional[str],
    ) -> None:
        self.comprobante_id = comprobante_id
        self.tipo_comprobante = tipo_comprobante
        self.numero_comprobante = numero_comprobante
        self.fecha_emision = fecha_emision
        self.monto_total = monto_total
        self.url_archivo = url_archivo


class ObtenerEstadoCuentaDetalladoCU:
    """
    Caso de Uso: Obtener estado de cuenta detallado de un alumno
    
    Adaptado para usar los métodos EXISTENTES en ports.py:
    - IPagoRepository.listar(alumno_id=X)
    - IComprobanteRepository.listar(sede_id=X) + filtro manual
    - IPlanCuotaRepository.listar_por_plan(plan_pago_id) + obtención previa del plan
    - ICalculadorDescuento.calcular_disponible(alumno_id, "TOTAL")
    - IEstadoCuentaNinoRepository.obtener_por_alumno(alumno_id) -> Dict[str, Any]
    """
    
    def __init__(
        self,
        alumno_repo: AlumnoRepositoryPort,
        estado_cuenta_repo: IEstadoCuentaNinoRepository,
        pago_repo: IPagoRepository,
        comprobante_repo: IComprobanteRepository,
        calculador_descuento: ICalculadorDescuento,
        cuota_repo: IPlanCuotaRepository,
    ) -> None:
        self.alumno_repo = alumno_repo
        self.estado_cuenta_repo = estado_cuenta_repo
        self.pago_repo = pago_repo
        self.comprobante_repo = comprobante_repo
        self.calculador_descuento = calculador_descuento
        self.cuota_repo = cuota_repo
    
    async def execute(self, alumno_id: int, sede_id: int) -> EstadoCuentaDetalladoDTO:
        """
        Ejecuta el caso de uso
        
        Args:
            alumno_id: ID del alumno
            sede_id: ID de la sede (validación RBAC)
        
        Returns:
            EstadoCuentaDetalladoDTO con información completa
        
        Raises:
            AlumnoNoEncontradoError: Si el alumno no existe o no pertenece a la sede
            EstadoCuentaNoEncontradoError: Si no tiene estado de cuenta configurado
        """
        # 1. Validar alumno y pertenencia a sede
        alumno_dict: Dict[str, Any] = await self._validar_alumno(alumno_id, sede_id)
        
        # 2. Obtener estado de cuenta
        estado_cuenta: Dict[str, Any] = await self._obtener_estado_cuenta(alumno_id)
        
        # 3. Obtener cuotas del plan de pago (requiere plan_pago_id primero)
        cuotas: List[CuotaDetalleDTO] = await self._obtener_cuotas_detalle(alumno_id, estado_cuenta)
        
        # 4. Obtener pagos realizados (usando listar con alumno_id)
        pagos: List[PagoDetalleDTO] = await self._obtener_pagos_detalle(alumno_id, sede_id)
        
        # 5. Obtener comprobantes emitidos (listar + filtro manual)
        comprobantes: List[ComprobanteDetalleDTO] = await self._obtener_comprobantes_detalle(alumno_id, sede_id)
        
        # 6. Calcular descuentos totales (usando calcular_disponible)
        descuentos: Decimal = await self.calculador_descuento.calcular_disponible(
            alumno_id, 
            "HERMANOS"  # ⚠️ Tu ports requiere tipo de descuento
        )
        
        # 7. Calcular totales financieros
        deuda_total: Decimal = Decimal(str(estado_cuenta.get("total_deuda", 0))) - descuentos
        total_pagado: Decimal = Decimal(str(estado_cuenta.get("total_pagado", 0)))
        saldo_pendiente: Decimal = Decimal(str(estado_cuenta.get("saldo_pendiente", 0)))
        
        # 8. Construir DTO de respuesta
        return EstadoCuentaDetalladoDTO(
            alumno_id=alumno_dict["id"],
            alumno_nombre_completo=f"{alumno_dict['nombre']} {alumno_dict['apellidos']}",
            fecha_consulta=datetime.now(),
            deuda_total=deuda_total,
            total_pagado=total_pagado,
            saldo_pendiente=saldo_pendiente,
            descuentos_aplicados=descuentos,
            cuotas=cuotas,
            pagos_realizados=pagos,
            comprobantes=comprobantes,
        )
    
    async def _validar_alumno(self, alumno_id: int, sede_id: int) -> Dict[str, Any]:
        """Valida que el alumno existe y pertenece a la sede"""
        # ⚠️ Asumiendo que tu IAlumnoRepository también retorna Dict
        alumno: Optional[Dict[str, Any]] = await self.alumno_repo.obtener_por_id(alumno_id)
        
        if not alumno:
            raise AlumnoNoEncontradoError(f"Alumno {alumno_id} no encontrado")
        
        if alumno.get("sede_id") != sede_id:
            raise AlumnoNoEncontradoError(
                f"Alumno {alumno_id} no pertenece a la sede {sede_id}"
            )
        
        return alumno
    
    async def _obtener_estado_cuenta(self, alumno_id: int) -> Dict[str, Any]:
        """Obtiene el estado de cuenta del alumno"""
        estado: Optional[Dict[str, Any]] = await self.estado_cuenta_repo.obtener_por_alumno(alumno_id)
        
        if not estado:
            raise EstadoCuentaNoEncontradoError(
                f"Estado de cuenta no encontrado para alumno {alumno_id}"
            )
        
        return estado
    
    async def _obtener_cuotas_detalle(
        self, 
        alumno_id: int, 
        estado_cuenta: Dict[str, Any]
    ) -> List[CuotaDetalleDTO]:
        """
        Obtiene detalle de cuotas del plan de pago
        
        ⚠️ PROBLEMA: Tu ports.listar_por_plan() requiere plan_pago_id
        SOLUCIÓN: Primero obtener plan_pago_id del estado_cuenta o de alumno
        """
        # Obtener plan_pago_id (asumiendo que está en estado_cuenta)
        plan_pago_id: Optional[int] = estado_cuenta.get("plan_pago_id")
        
        if not plan_pago_id:
            # Si no hay plan de pago, retornar lista vacía
            return []
        
        # Listar cuotas del plan
        cuotas_dict: List[Dict[str, Any]] = await self.cuota_repo.listar_por_plan(
            plan_pago_id=plan_pago_id,
            estado=None  # Todas las cuotas
        )
        
        cuotas_dto: List[CuotaDetalleDTO] = []
        for cuota in cuotas_dict:
            # Calcular estado de la cuota (PENDIENTE/PAGADA/VENCIDA)
            estado_cuota: str = self._calcular_estado_cuota(cuota)
            
            # Calcular días de mora (solo si vencida y no pagada)
            dias_mora: int = self._calcular_dias_mora(cuota)
            
            cuotas_dto.append(
                CuotaDetalleDTO(
                    cuota_id=cuota["id"],
                    numero_cuota=cuota["numero_cuota"],
                    monto=Decimal(str(cuota["monto"])),
                    fecha_vencimiento=cuota["fecha_vencimiento"],
                    estado=estado_cuota,
                    monto_pagado=Decimal(str(cuota.get("monto_pagado", 0))),
                    dias_mora=dias_mora,
                )
            )
        
        return cuotas_dto
    
    async def _obtener_pagos_detalle(self, alumno_id: int, sede_id: int) -> List[PagoDetalleDTO]:
        """
        Obtiene detalle de pagos del alumno
        
        ✅ SOLUCIÓN: Usar listar() con alumno_id como parámetro
        """
        pagos_dict: List[Dict[str, Any]] = await self.pago_repo.listar(
            sede_id=sede_id,
            alumno_id=alumno_id,  # ✅ Tu ports acepta alumno_id
            incluir_anulados=False,
            limit=1000  # Aumentar límite para obtener todos los pagos
        )
        
        pagos_dto: List[PagoDetalleDTO] = []
        for pago in pagos_dict:
            # Obtener nombre de categoría de pago (si existe en dict)
            categoria_nombre: str = pago.get("categoria_nombre", "Sin categoría")
            
            pagos_dto.append(
                PagoDetalleDTO(
                    pago_id=pago["id"],
                    fecha_pago=pago["fecha_pago"],
                    monto=Decimal(str(pago["monto_pagado"])),
                    metodo_pago=pago["metodo_pago"],
                    categoria_nombre=categoria_nombre,
                    nro_recibo=pago.get("numero_comprobante"),
                    observaciones=pago.get("observaciones"),
                )
            )
        
        return pagos_dto
    
    async def _obtener_comprobantes_detalle(
        self, 
        alumno_id: int, 
        sede_id: int
    ) -> List[ComprobanteDetalleDTO]:
        """
        Obtiene detalle de comprobantes del alumno
        
        ⚠️ PROBLEMA: Tu ports.listar() NO acepta alumno_id
        SOLUCIÓN: Listar todos de la sede y filtrar manualmente por alumno_id
        """
        # Listar todos los comprobantes de la sede
        comprobantes_dict: List[Dict[str, Any]] = await self.comprobante_repo.listar(
            sede_id=sede_id,
            tipo=None,
            limit=1000
        )
        
        # Filtrar manualmente por alumno_id
        comprobantes_alumno = [
            comp for comp in comprobantes_dict 
            if comp.get("alumno_id") == alumno_id
        ]
        
        comprobantes_dto: List[ComprobanteDetalleDTO] = []
        for comp in comprobantes_alumno:
            comprobantes_dto.append(
                ComprobanteDetalleDTO(
                    comprobante_id=comp["id"],
                    tipo_comprobante=comp["tipo"],
                    numero_comprobante=comp["numero"],
                    fecha_emision=comp["fecha_emision"],
                    monto_total=Decimal(str(comp["monto"])),
                    url_archivo=comp.get("ruta_archivo"),
                )
            )
        
        return comprobantes_dto
    
    def _calcular_estado_cuota(self, cuota: Dict[str, Any]) -> str:
        """
        Calcula el estado actual de una cuota según reglas de negocio
        
        Reglas:
        - PAGADA: monto_pagado >= monto
        - VENCIDA: fecha_vencimiento < hoy Y monto_pagado < monto
        - PENDIENTE: fecha_vencimiento >= hoy Y monto_pagado < monto
        """
        monto_pagado: Decimal = Decimal(str(cuota.get("monto_pagado", 0)))
        monto: Decimal = Decimal(str(cuota["monto"]))
        fecha_vencimiento: date = cuota["fecha_vencimiento"]
        
        # Cuota completamente pagada
        if monto_pagado >= monto:
            return "PAGADA"
        
        # Cuota vencida y no pagada
        if fecha_vencimiento < date.today():
            return "VENCIDA"
        
        # Cuota pendiente de pago
        return "PENDIENTE"
    
    def _calcular_dias_mora(self, cuota: Dict[str, Any]) -> int:
        """
        Calcula los días de mora de una cuota
        
        Reglas:
        - Mora = 0 si cuota está pagada (monto_pagado >= monto)
        - Mora = 0 si cuota no está vencida (fecha_vencimiento >= hoy)
        - Mora = (hoy - fecha_vencimiento).days si vencida y no pagada
        """
        monto_pagado: Decimal = Decimal(str(cuota.get("monto_pagado", 0)))
        monto: Decimal = Decimal(str(cuota["monto"]))
        fecha_vencimiento: date = cuota["fecha_vencimiento"]
        
        # Sin mora si está pagada
        if monto_pagado >= monto:
            return 0
        
        # Sin mora si no está vencida
        if fecha_vencimiento >= date.today():
            return 0
        
        # Calcular días transcurridos desde vencimiento
        diferencia = date.today() - fecha_vencimiento
        dias_mora: int = diferencia.days
        
        return max(0, dias_mora)
