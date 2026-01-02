"""
Caso de Uso: Obtener Reporte Detallado de Deudores
Endpoint: GET /api/v1/reportes/deudores/{alumno_id}
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Detalle completo de deuda de un alumno
2. Historial de pagos y cuotas vencidas
3. Incluye datos de contacto de tutores
4. Estado de cuenta detallado
"""

from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any, Optional

from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort
from app.kernel.domain.finanzas.ports import (
    IEstadoCuentaNinoRepository,
    IPagoRepository,
    IPlanCuotaRepository,
)


class CuotaDeudaDTO:
    """DTO para cuota vencida"""
    
    def __init__(
        self,
        cuota_id: int,
        numero_cuota: int,
        monto_original: Decimal,
        monto_pagado: Decimal,
        monto_pendiente: Decimal,
        fecha_vencimiento: date,
        dias_mora: int,
    ) -> None:
        self.cuota_id = cuota_id
        self.numero_cuota = numero_cuota
        self.monto_original = monto_original
        self.monto_pagado = monto_pagado
        self.monto_pendiente = monto_pendiente
        self.fecha_vencimiento = fecha_vencimiento
        self.dias_mora = dias_mora


class PagoHistoricoDTO:
    """DTO para pago histórico"""
    
    def __init__(
        self,
        pago_id: int,
        fecha_pago: datetime,
        monto: Decimal,
        metodo_pago: str,
        nro_recibo: Optional[str],
    ) -> None:
        self.pago_id = pago_id
        self.fecha_pago = fecha_pago
        self.monto = monto
        self.metodo_pago = metodo_pago
        self.nro_recibo = nro_recibo


class ReporteDeudorDTO:
    """DTO de respuesta"""
    
    def __init__(
        self,
        alumno_id: int,
        alumno_nombre_completo: str,
        telefono_tutor: Optional[str],
        email_tutor: Optional[str],
        deuda_total: Decimal,
        total_pagado: Decimal,
        saldo_pendiente: Decimal,
        cuotas_vencidas: List[CuotaDeudaDTO],
        historial_pagos: List[PagoHistoricoDTO],
        dias_mora_maximos: int,
        fecha_ultima_cuota_vencida: Optional[date],
    ) -> None:
        self.alumno_id = alumno_id
        self.alumno_nombre_completo = alumno_nombre_completo
        self.telefono_tutor = telefono_tutor
        self.email_tutor = email_tutor
        self.deuda_total = deuda_total
        self.total_pagado = total_pagado
        self.saldo_pendiente = saldo_pendiente
        self.cuotas_vencidas = cuotas_vencidas
        self.historial_pagos = historial_pagos
        self.dias_mora_maximos = dias_mora_maximos
        self.fecha_ultima_cuota_vencida = fecha_ultima_cuota_vencida


class ObtenerReporteDeudoresCU:
    """Caso de Uso: Obtener reporte detallado de deudor"""
    
    def __init__(
        self,
        alumno_repo: AlumnoRepositoryPort,
        estado_cuenta_repo: IEstadoCuentaNinoRepository,
        pago_repo: IPagoRepository,
        cuota_repo: IPlanCuotaRepository,
    ) -> None:
        self.alumno_repo = alumno_repo
        self.estado_cuenta_repo = estado_cuenta_repo
        self.pago_repo = pago_repo
        self.cuota_repo = cuota_repo
    
    async def execute(
        self,
        alumno_id: int,
        sede_id: int,
    ) -> ReporteDeudorDTO:
        """
        Obtiene reporte detallado de deuda de un alumno
        
        Args:
            alumno_id: ID del alumno
            sede_id: ID de la sede (validación RBAC)
        
        Returns:
            ReporteDeudorDTO con información completa de deuda
        """
        # 1. Obtener datos del alumno
        alumno_dict: Optional[Dict[str, Any]] = await self.alumno_repo.obtener_por_id(alumno_id)
        
        if not alumno_dict or alumno_dict.get("sede_id") != sede_id:
            raise ValueError(f"Alumno {alumno_id} no encontrado en sede {sede_id}")
        
        # 2. Obtener estado de cuenta
        estado_cuenta: Optional[Dict[str, Any]] = await self.estado_cuenta_repo.obtener_por_alumno(alumno_id)
        
        if not estado_cuenta:
            raise ValueError(f"Alumno {alumno_id} no tiene estado de cuenta")
        
        # 3. Obtener cuotas vencidas
        plan_pago_id: Optional[int] = estado_cuenta.get("plan_pago_id")
        cuotas_vencidas_dto: List[CuotaDeudaDTO] = []
        dias_mora_maximos: int = 0
        fecha_ultima_vencida: Optional[date] = None
        
        if plan_pago_id:
            cuotas: List[Dict[str, Any]] = await self.cuota_repo.listar_por_plan(
                plan_pago_id=plan_pago_id,
                estado=None
            )
            
            for cuota in cuotas:
                if self._es_cuota_vencida(cuota):
                    monto_original: Decimal = Decimal(str(cuota["monto"]))
                    monto_pagado: Decimal = Decimal(str(cuota.get("monto_pagado", 0)))
                    monto_pendiente: Decimal = monto_original - monto_pagado
                    dias_mora: int = self._calcular_dias_mora(cuota)
                    
                    cuotas_vencidas_dto.append(
                        CuotaDeudaDTO(
                            cuota_id=cuota["id"],
                            numero_cuota=cuota["numero_cuota"],
                            monto_original=monto_original,
                            monto_pagado=monto_pagado,
                            monto_pendiente=monto_pendiente,
                            fecha_vencimiento=cuota["fecha_vencimiento"],
                            dias_mora=dias_mora,
                        )
                    )
                    
                    dias_mora_maximos = max(dias_mora_maximos, dias_mora)
                    
                    if fecha_ultima_vencida is None or cuota["fecha_vencimiento"] > fecha_ultima_vencida:
                        fecha_ultima_vencida = cuota["fecha_vencimiento"]
        
        # 4. Obtener historial de pagos
        pagos: List[Dict[str, Any]] = await self.pago_repo.listar(
            sede_id=sede_id,
            alumno_id=alumno_id,
            incluir_anulados=False,
            limit=1000
        )
        
        historial_dto: List[PagoHistoricoDTO] = [
            PagoHistoricoDTO(
                pago_id=p["id"],
                fecha_pago=p["fecha_pago"],
                monto=Decimal(str(p.get("monto_pagado", 0))),
                metodo_pago=p.get("metodo_pago", "No especificado"),
                nro_recibo=p.get("numero_comprobante"),
            )
            for p in pagos
        ]
        
        # Ordenar por fecha descendente
        historial_dto.sort(key=lambda x: x.fecha_pago, reverse=True)
        
        return ReporteDeudorDTO(
            alumno_id=alumno_id,
            alumno_nombre_completo=f"{alumno_dict['nombre']} {alumno_dict['apellidos']}",
            telefono_tutor=alumno_dict.get("telefono_tutor"),
            email_tutor=alumno_dict.get("email_tutor"),
            deuda_total=Decimal(str(estado_cuenta.get("total_deuda", 0))),
            total_pagado=Decimal(str(estado_cuenta.get("total_pagado", 0))),
            saldo_pendiente=Decimal(str(estado_cuenta.get("saldo_pendiente", 0))),
            cuotas_vencidas=cuotas_vencidas_dto,
            historial_pagos=historial_dto,
            dias_mora_maximos=dias_mora_maximos,
            fecha_ultima_cuota_vencida=fecha_ultima_vencida,
        )
    
    def _es_cuota_vencida(self, cuota: Dict[str, Any]) -> bool:
        """Determina si una cuota está vencida"""
        monto_pagado: Decimal = Decimal(str(cuota.get("monto_pagado", 0)))
        monto: Decimal = Decimal(str(cuota["monto"]))
        fecha_vencimiento: date = cuota["fecha_vencimiento"]
        
        return fecha_vencimiento < date.today() and monto_pagado < monto
    
    def _calcular_dias_mora(self, cuota: Dict[str, Any]) -> int:
        """Calcula días de mora de una cuota"""
        fecha_vencimiento: date = cuota["fecha_vencimiento"]
        diferencia = date.today() - fecha_vencimiento
        return max(0, diferencia.days)
