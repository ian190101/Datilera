# app/kernel/application/inventario/devolver_prestamo.py
from __future__ import annotations
from datetime import date
from pydantic import BaseModel

from app.infrastructure.db.repositories.inventario.prestamos_uniformes_repo import PrestamosUniformesRepository
from app.kernel.domain.exceptions import EntityNotFoundException

class DevolverPrestamoRequest(BaseModel):
    fecha_devolucion: date | None = None

class DevolverPrestamo:
    def __init__(self, repo: PrestamosUniformesRepository):
        self.repo = repo

    async def execute(self, prestamo_id: int, req: DevolverPrestamoRequest) -> None:
        prestamo = await self.repo.get(prestamo_id)
        if not prestamo:
            raise EntityNotFoundException(f"Préstamo {prestamo_id} no encontrado.")
        if prestamo.devuelto:
            return
        fecha = req.fecha_devolucion or date.today()
        await self.repo.update(prestamo_id, {"devuelto": True, "fecha_devolucion": fecha})
