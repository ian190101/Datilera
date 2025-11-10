# app/kernel/domain/finanzas/conciliacion_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional


class EstadoConciliacion(str, Enum):
    PENDIENTE = "pendiente"
    DEPOSITADO = "depositado"
    TRANSFERIDO = "transferido"
    VERIFICADO = "verificado"


@dataclass
class Conciliacion:
    """
    Conciliación de depósitos/transferencias semanales (directora -> cuenta dueña).

    Historias:
    - Flujo de estados: PENDIENTE -> DEPOSITADO -> TRANSFERIDO -> VERIFICADO.
    - Se programa típicamente en viernes; registra fechas y observaciones.
    """
    id: int
    sede_id: int
    periodo_semana_inicio: date
    periodo_semana_fin: date
    estado: EstadoConciliacion = EstadoConciliacion.PENDIENTE
    fecha_depositado: Optional[datetime] = None
    fecha_transferido: Optional[datetime] = None
    fecha_verificado: Optional[datetime] = None
    observaciones: Optional[str] = None
    creado_en: datetime = None

    def __post_init__(self):
        if self.periodo_semana_fin < self.periodo_semana_inicio:
            raise ValueError("Rango de semana inválido en conciliación.")
        self.creado_en = self.creado_en or datetime.utcnow()

    def avanzar(self, nuevo_estado: EstadoConciliacion) -> None:
        orden = [EstadoConciliacion.PENDIENTE, EstadoConciliacion.DEPOSITADO,
                 EstadoConciliacion.TRANSFERIDO, EstadoConciliacion.VERIFICADO]
        if orden.index(nuevo_estado) < orden.index(self.estado):
            raise ValueError("No se puede retroceder de estado en la conciliación.")
        self.estado = nuevo_estado
        if nuevo_estado == EstadoConciliacion.DEPOSITADO:
            self.fecha_depositado = datetime.utcnow()
        elif nuevo_estado == EstadoConciliacion.TRANSFERIDO:
            self.fecha_transferido = datetime.utcnow()
        elif nuevo_estado == EstadoConciliacion.VERIFICADO:
            self.fecha_verificado = datetime.utcnow()