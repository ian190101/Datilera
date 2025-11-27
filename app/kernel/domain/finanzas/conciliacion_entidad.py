# app/kernel/domain/finanzas/conciliacion_entidad.py
from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class EstadoConciliacion(str, Enum):
    PENDIENTE = "pendiente"
    DEPOSITADO = "depositado"
    TRANSFERIDO = "transferido"
    VERIFICADO = "verificado"

class Conciliacion(BaseModel):
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
    
    # Reemplaza la asignación en __post_init__
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode='after')
    def validar_rango_fechas(self) -> Conciliacion:
        """Valida que la fecha de fin no sea anterior a la de inicio"""
        if self.periodo_semana_fin < self.periodo_semana_inicio:
            raise ValueError("Rango de semana inválido en conciliación.")
        return self

    def avanzar(self, nuevo_estado: EstadoConciliacion) -> None:
        """
        Avanza el estado de la conciliación registrando la fecha del evento.
        Valida que no se retroceda en el flujo.
        """
        orden = [
            EstadoConciliacion.PENDIENTE, 
            EstadoConciliacion.DEPOSITADO,
            EstadoConciliacion.TRANSFERIDO, 
            EstadoConciliacion.VERIFICADO
        ]
        
        # Validar flujo progresivo
        if orden.index(nuevo_estado) < orden.index(self.estado):
            raise ValueError("No se puede retroceder de estado en la conciliación.")
        
        self.estado = nuevo_estado
        now = datetime.utcnow()
        
        # Registrar timestamps según el estado
        if nuevo_estado == EstadoConciliacion.DEPOSITADO:
            self.fecha_depositado = now
        elif nuevo_estado == EstadoConciliacion.TRANSFERIDO:
            self.fecha_transferido = now
        elif nuevo_estado == EstadoConciliacion.VERIFICADO:
            self.fecha_verificado = now
