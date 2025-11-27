# app/kernel/application/sede/obtener_sede.py
from app.kernel.domain.seguridad.sede_entidad import Sede
from app.kernel.domain.seguridad.errors import SedeNoEncontrada
from app.kernel.domain.seguridad.ports import AbstractSedeRepository

class ObtenerSede:
    def __init__(self, sede_repo: AbstractSedeRepository):
        self.sede_repo = sede_repo

    async def execute(self, sede_id: int) -> Sede:
        sede = await self.sede_repo.get(sede_id)
        if not sede:
            raise SedeNoEncontrada(f"Sede con ID {sede_id} no encontrada")
        return Sede.model_validate(sede)