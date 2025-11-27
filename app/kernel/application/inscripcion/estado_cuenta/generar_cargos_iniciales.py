# app/application/inscripcion/estado_cuenta/generar_cargos_iniciales.py
from typing import Protocol, Optional
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class EstadoCuentaServicePort(Protocol):
    async def crear_cargo(self, alumno_id: int, fecha: date, categoria_pago_id: Optional[int], monto: Decimal, referencia: str, observaciones: Optional[str]) -> int: ...

class GenerarCargosInicialesCommand(BaseModel):
    alumno_id: int
    fecha: date
    monto_inicial: Decimal
    categoria_pago_id: Optional[int] = None
    referencia: str = "inscripcion:inicial"
    observaciones: Optional[str] = None

class GenerarCargosInicialesUseCase:
    def __init__(self, estado_cuenta_service: EstadoCuentaServicePort):
        self.estado_cuenta_service = estado_cuenta_service

    async def execute(self, cmd: GenerarCargosInicialesCommand) -> int:
        return await self.estado_cuenta_service.crear_cargo(
            alumno_id=cmd.alumno_id,
            fecha=cmd.fecha,
            categoria_pago_id=cmd.categoria_pago_id,
            monto=cmd.monto_inicial,
            referencia=cmd.referencia,
            observaciones=cmd.observaciones,
        )
