"""
Caso de Uso: Verificar si un Alumno es Moroso
Endpoint: GET /api/v1/finanzas/estado-cuenta/{alumno_id}/moroso
Autor: Arquitecto Senior
Fecha: 2025-12-03

Reglas de Negocio (según HU):
1. Un alumno es MOROSO si tiene cuotas vencidas (fecha_vencimiento < hoy)
2. Cuota vencida: monto_pagado < monto Y fecha_vencimiento < hoy
3. Se consideran solo cuotas de planes activos
4. Retorna días de mora máximos y total adeudado vencido
5. Estado: MOROSO | AL_DIA | SIN_PLAN
"""

from decimal import Decimal
from datetime import date
from typing import Dict, Any, Optional, List

from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort
from app.kernel.domain.finanzas.ports import (
    IEstadoCuentaNinoRepository,
    IPlanCuotaRepository,
)
from app.kernel.domain.alumnos.errors import AlumnoNoEncontradoError
from app.kernel.domain.finanzas.errors import EstadoCuentaNoEncontradoError


class EstadoMorosoDTO:
    """DTO de respuesta para verificación de morosidad"""
    
    def __init__(
        self,
        alumno_id: int,
        alumno_nombre_completo: str,
        es_moroso: bool,
        estado: str,  # MOROSO | AL_DIA | SIN_PLAN
        dias_mora_maximos: int,
        total_vencido: Decimal,
        cantidad_cuotas_vencidas: int,
        fecha_vencimiento_mas_antigua: Optional[date],
    ) -> None:
        self.alumno_id = alumno_id
        self.alumno_nombre_completo = alumno_nombre_completo
        self.es_moroso = es_moroso
        self.estado = estado
        self.dias_mora_maximos = dias_mora_maximos
        self.total_vencido = total_vencido
        self.cantidad_cuotas_vencidas = cantidad_cuotas_vencidas
        self.fecha_vencimiento_mas_antigua = fecha_vencimiento_mas_antigua


class VerificarAlumnoMorosoCU:
    """
    Caso de Uso: Verificar si un alumno está en estado de morosidad
    
    Adaptado para usar ports.py actual:
    - IEstadoCuentaNinoRepository.obtener_por_alumno(alumno_id) -> Dict
    - IPlanCuotaRepository.listar_por_plan(plan_pago_id) -> List[Dict]
    """
    
    def __init__(
        self,
        alumno_repo: AlumnoRepositoryPort,
        estado_cuenta_repo: IEstadoCuentaNinoRepository,
        cuota_repo: IPlanCuotaRepository,
    ) -> None:
        self.alumno_repo = alumno_repo
        self.estado_cuenta_repo = estado_cuenta_repo
        self.cuota_repo = cuota_repo
    
    async def execute(self, alumno_id: int, sede_id: int) -> EstadoMorosoDTO:
        """
        Verifica el estado de morosidad de un alumno
        
        Args:
            alumno_id: ID del alumno a verificar
            sede_id: ID de la sede (validación RBAC)
        
        Returns:
            EstadoMorosoDTO con información de morosidad
        
        Raises:
            AlumnoNoEncontradoError: Si el alumno no existe o no pertenece a la sede
            EstadoCuentaNoEncontradoError: Si no tiene estado de cuenta
        """
        # 1. Validar alumno
        alumno_dict: Dict[str, Any] = await self._validar_alumno(alumno_id, sede_id)
        
        # 2. Obtener estado de cuenta
        estado_cuenta: Dict[str, Any] = await self._obtener_estado_cuenta(alumno_id)
        
        # 3. Obtener plan_pago_id
        plan_pago_id: Optional[int] = estado_cuenta.get("plan_pago_id")
        
        if not plan_pago_id:
            # Sin plan de pago activo
            return EstadoMorosoDTO(
                alumno_id=alumno_dict["id"],
                alumno_nombre_completo=f"{alumno_dict['nombre']} {alumno_dict['apellidos']}",
                es_moroso=False,
                estado="SIN_PLAN",
                dias_mora_maximos=0,
                total_vencido=Decimal("0"),
                cantidad_cuotas_vencidas=0,
                fecha_vencimiento_mas_antigua=None,
            )
        
        # 4. Listar cuotas del plan
        cuotas: List[Dict[str, Any]] = await self.cuota_repo.listar_por_plan(
            plan_pago_id=plan_pago_id,
            estado=None  # Todas las cuotas
        )
        
        # 5. Filtrar cuotas vencidas
        cuotas_vencidas: List[Dict[str, Any]] = [
            cuota for cuota in cuotas
            if self._es_cuota_vencida(cuota)
        ]
        
        # 6. Calcular métricas de morosidad
        if not cuotas_vencidas:
            return EstadoMorosoDTO(
                alumno_id=alumno_dict["id"],
                alumno_nombre_completo=f"{alumno_dict['nombre']} {alumno_dict['apellidos']}",
                es_moroso=False,
                estado="AL_DIA",
                dias_mora_maximos=0,
                total_vencido=Decimal("0"),
                cantidad_cuotas_vencidas=0,
                fecha_vencimiento_mas_antigua=None,
            )
        
        # 7. Calcular días de mora máximos y total vencido
        dias_mora_maximos: int = max(
            self._calcular_dias_mora(cuota) for cuota in cuotas_vencidas
        )
        
        total_vencido: Decimal = sum(
            (self._calcular_monto_vencido(cuota) for cuota in cuotas_vencidas),
            Decimal("0")
        )
        
        fecha_mas_antigua: Optional[date] = min(
            cuota["fecha_vencimiento"] for cuota in cuotas_vencidas
        )
        
        return EstadoMorosoDTO(
            alumno_id=alumno_dict["id"],
            alumno_nombre_completo=f"{alumno_dict['nombre']} {alumno_dict['apellidos']}",
            es_moroso=True,
            estado="MOROSO",
            dias_mora_maximos=dias_mora_maximos,
            total_vencido=total_vencido,
            cantidad_cuotas_vencidas=len(cuotas_vencidas),
            fecha_vencimiento_mas_antigua=fecha_mas_antigua,
        )
    
    async def _validar_alumno(self, alumno_id: int, sede_id: int) -> Dict[str, Any]:
        """Valida que el alumno existe y pertenece a la sede"""
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
    
    def _es_cuota_vencida(self, cuota: Dict[str, Any]) -> bool:
        """
        Determina si una cuota está vencida
        
        Reglas:
        - Vencida: fecha_vencimiento < hoy Y monto_pagado < monto
        """
        monto_pagado: Decimal = Decimal(str(cuota.get("monto_pagado", 0)))
        monto: Decimal = Decimal(str(cuota["monto"]))
        fecha_vencimiento: date = cuota["fecha_vencimiento"]
        
        return fecha_vencimiento < date.today() and monto_pagado < monto
    
    def _calcular_dias_mora(self, cuota: Dict[str, Any]) -> int:
        """Calcula los días de mora de una cuota vencida"""
        fecha_vencimiento: date = cuota["fecha_vencimiento"]
        diferencia = date.today() - fecha_vencimiento
        return max(0, diferencia.days)
    
    def _calcular_monto_vencido(self, cuota: Dict[str, Any]) -> Decimal:
        """Calcula el monto vencido de una cuota (monto - monto_pagado)"""
        monto: Decimal = Decimal(str(cuota["monto"]))
        monto_pagado: Decimal = Decimal(str(cuota.get("monto_pagado", 0)))
        return max(Decimal("0"), monto - monto_pagado)
