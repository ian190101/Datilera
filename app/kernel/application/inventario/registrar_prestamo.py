# app/kernel/application/inventario/registrar_prestamo.py
from __future__ import annotations
from datetime import date
from pydantic import BaseModel, Field, ConfigDict

from app.infrastructure.db.repositories.inventario.prestamos_uniformes_repo import PrestamosUniformesRepository
from app.infrastructure.db.models.inventario import PrestamoUniforme as PrestamoModel

class RegistrarPrestamoRequest(BaseModel):
    alumno_id: int
    item_id: int
    fecha_prestamo: date = Field(default_factory=date.today)

class PrestamoResponse(BaseModel):
    id: int
    alumno_id: int
    item_id: int
    fecha_prestamo: date
    devuelto: bool
    fecha_devolucion: date | None = None
    model_config = ConfigDict(from_attributes=True)

class RegistrarPrestamo:
    def __init__(self, repo: PrestamosUniformesRepository):
        self.repo = repo

    async def execute(self, req: RegistrarPrestamoRequest) -> PrestamoResponse:
        prestamo = await self.repo.create(PrestamoModel(
            alumno_id=req.alumno_id,
            item_id=req.item_id,
            fecha_prestamo=req.fecha_prestamo,
            devuelto=False
        ))
        return PrestamoResponse.model_validate(prestamo, from_attributes=True)
