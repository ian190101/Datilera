# app/kernel/application/sede/desactivar_sede.py
from app.kernel.domain.seguridad.sede_entidad import Sede
from app.kernel.domain.seguridad.errors import SedeNoEncontrada
from app.kernel.domain.seguridad.ports import AbstractSedeRepository

class EliminarSede:
    def __init__(self, sede_repo: AbstractSedeRepository):
        self.sede_repo = sede_repo

    async def execute(self, sede_id: int) -> Sede:
        ok = await self.sede_repo.delete_soft(sede_id)
        if not ok:
            raise SedeNoEncontrada(f"Sede con ID {sede_id} no encontrada")
        
    
