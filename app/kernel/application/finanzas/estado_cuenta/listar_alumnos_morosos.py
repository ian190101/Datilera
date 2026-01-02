#app/kernel/application/finanzas/estado_cuenta/listar_alumnos_morosos.py
"""
Reglas de Negocio (según HU):
1. Lista alumnos con saldo_pendiente > 0 y cuotas vencidas
2. Ordenados por días de mora descendente (más morosos primero)
3. Incluye: nombre, días_mora, total_vencido, última_cuota_vencida
4. Paginación: limit/offset
5. Filtros: sede_id, días_mora_minimos
"""

from decimal import Decimal
from datetime import date
from typing import List, Dict, Any, Optional

from app.kernel.domain.finanzas.ports import (
    IEstadoCuentaNinoRepository,
    IPlanCuotaRepository,
)
from app.kernel.domain.alumnos.ports import AlumnoRepositoryPort


class AlumnoMorosoItemDTO:
    """DTO de respuesta para un alumno moroso en la lista"""
    
    def __init__(
        self,
        alumno_id: int,
        alumno_nombre_completo: str,
        dias_mora_maximos: int,
        total_vencido: Decimal,
        saldo_pendiente: Decimal,
        cantidad_cuotas_vencidas: int,
        fecha_ultima_cuota_vencida: date,
        telefono_tutor: Optional[str],
    ) -> None:
        self.alumno_id = alumno_id
        self.alumno_nombre_completo = alumno_nombre_completo
        self.dias_mora_maximos = dias_mora_maximos
        self.total_vencido = total_vencido
        self.saldo_pendiente = saldo_pendiente
        self.cantidad_cuotas_vencidas = cantidad_cuotas_vencidas
        self.fecha_ultima_cuota_vencida = fecha_ultima_cuota_vencida
        self.telefono_tutor = telefono_tutor


class ListaAlumnosMorososDTO:
    """DTO de respuesta para listado paginado de alumnos morosos"""
    
    def __init__(
        self,
        alumnos: List[AlumnoMorosoItemDTO],
        total: int,
        pagina_actual: int,
        total_paginas: int,
    ) -> None:
        self.alumnos = alumnos
        self.total = total
        self.pagina_actual = pagina_actual
        self.total_paginas = total_paginas


class ListarAlumnosMorososCU:
    """
    Caso de Uso: Listar alumnos morosos de una sede
    
    Adaptado para usar ports.py actual:
    - IEstadoCuentaNinoRepository.listar_deudores(sede_id) -> List[Dict]
    - IPlanCuotaRepository.listar_por_plan(plan_pago_id) por cada alumno
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
    
    async def execute(
        self,
        sede_id: int,
        dias_mora_minimos: int = 1,
        limit: int = 50,
        offset: int = 0,
    ) -> ListaAlumnosMorososDTO:
        """
        Lista alumnos morosos de una sede
        
        Args:
            sede_id: ID de la sede a consultar
            dias_mora_minimos: Mínimo de días de mora para considerar (default: 1)
            limit: Cantidad de resultados por página
            offset: Offset para paginación
        
        Returns:
            ListaAlumnosMorososDTO con listado paginado
        """
        # 1. Obtener alumnos con deuda de la sede
        alumnos_deudores: List[Dict[str, Any]] = await self.estado_cuenta_repo.listar_deudores(
            sede_id=sede_id,
            limite=1000  # Obtener todos para filtrar manualmente
        )
        
        # 2. Verificar morosidad de cada alumno
        alumnos_morosos: List[Dict[str, Any]] = []
        
        for estado_cuenta in alumnos_deudores:
            alumno_id: int = estado_cuenta["alumno_id"]
            plan_pago_id: Optional[int] = estado_cuenta.get("plan_pago_id")
            
            if not plan_pago_id:
                continue  # Sin plan de pago, saltar
            
            # Obtener cuotas del plan
            cuotas: List[Dict[str, Any]] = await self.cuota_repo.listar_por_plan(
                plan_pago_id=plan_pago_id,
                estado=None
            )
            
            # Filtrar cuotas vencidas
            cuotas_vencidas: List[Dict[str, Any]] = [
                c for c in cuotas if self._es_cuota_vencida(c)
            ]
            
            if not cuotas_vencidas:
                continue  # No tiene cuotas vencidas, saltar
            
            # Calcular días de mora máximos
            dias_mora: int = max(
                self._calcular_dias_mora(c) for c in cuotas_vencidas
            )
            
            if dias_mora < dias_mora_minimos:
                continue  # No alcanza el mínimo de días de mora
            
            # Calcular total vencido
            total_vencido: Decimal = sum(
                (self._calcular_monto_vencido(c) for c in cuotas_vencidas),
                Decimal("0")
            )
            
            # Fecha de última cuota vencida
            fecha_ultima_vencida: date = max(
                c["fecha_vencimiento"] for c in cuotas_vencidas
            )
            
            # Obtener datos del alumno
            alumno_dict: Optional[Dict[str, Any]] = await self.alumno_repo.obtener_por_id(alumno_id)
            
            if not alumno_dict:
                continue  # Alumno no encontrado, saltar
            
            alumnos_morosos.append({
                "alumno_id": alumno_id,
                "alumno_nombre_completo": f"{alumno_dict['nombre']} {alumno_dict['apellidos']}",
                "dias_mora_maximos": dias_mora,
                "total_vencido": total_vencido,
                "saldo_pendiente": Decimal(str(estado_cuenta.get("saldo_pendiente", 0))),
                "cantidad_cuotas_vencidas": len(cuotas_vencidas),
                "fecha_ultima_cuota_vencida": fecha_ultima_vencida,
                "telefono_tutor": alumno_dict.get("telefono_tutor"),
            })
        
        # 3. Ordenar por días de mora descendente
        alumnos_morosos.sort(
            key=lambda x: x["dias_mora_maximos"],
            reverse=True
        )
        
        # 4. Aplicar paginación manual
        total: int = len(alumnos_morosos)
        alumnos_pagina: List[Dict[str, Any]] = alumnos_morosos[offset:offset + limit]
        
        # 5. Construir DTOs
        alumnos_dto: List[AlumnoMorosoItemDTO] = [
            AlumnoMorosoItemDTO(
                alumno_id=a["alumno_id"],
                alumno_nombre_completo=a["alumno_nombre_completo"],
                dias_mora_maximos=a["dias_mora_maximos"],
                total_vencido=a["total_vencido"],
                saldo_pendiente=a["saldo_pendiente"],
                cantidad_cuotas_vencidas=a["cantidad_cuotas_vencidas"],
                fecha_ultima_cuota_vencida=a["fecha_ultima_cuota_vencida"],
                telefono_tutor=a["telefono_tutor"],
            )
            for a in alumnos_pagina
        ]
        
        total_paginas: int = (total + limit - 1) // limit if limit > 0 else 1
        pagina_actual: int = (offset // limit) + 1 if limit > 0 else 1
        
        return ListaAlumnosMorososDTO(
            alumnos=alumnos_dto,
            total=total,
            pagina_actual=pagina_actual,
            total_paginas=total_paginas,
        )
    
    def _es_cuota_vencida(self, cuota: Dict[str, Any]) -> bool:
        """Determina si una cuota está vencida"""
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
        """Calcula el monto vencido de una cuota"""
        monto: Decimal = Decimal(str(cuota["monto"]))
        monto_pagado: Decimal = Decimal(str(cuota.get("monto_pagado", 0)))
        return max(Decimal("0"), monto - monto_pagado)
