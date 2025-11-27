# app/application/inscripcion/alta_academica/alta_academica.py
from typing import Protocol
from pydantic import BaseModel
from datetime import date

class AsignacionAcademicaServicePort(Protocol):
    async def asignar_grupo_paralelo(self, alumno_id: int, sede_id: int, edad_meses: int) -> dict: ...

class AltaAcademicaCommand(BaseModel):
    alumno_id: int
    sede_id: int
    fecha_nacimiento: date
    fecha_referencia: date
    turno_id: int

class AltaAcademicaUseCase:
    def __init__(self, asignacion_service: AsignacionAcademicaServicePort):
        self.asignacion_service = asignacion_service

    async def execute(self, cmd: AltaAcademicaCommand) -> dict:
        edad_meses = (cmd.fecha_referencia.year - cmd.fecha_nacimiento.year) * 12 + (cmd.fecha_referencia.month - cmd.fecha_nacimiento.month)
        edad_meses = max(0, edad_meses)
        asignacion = await self.asignacion_service.asignar_grupo_paralelo(cmd.alumno_id, cmd.sede_id, edad_meses)
        return {"edad_meses": edad_meses, "asignacion": asignacion, "turno_id": cmd.turno_id}
