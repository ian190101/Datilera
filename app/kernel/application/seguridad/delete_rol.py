
from app.infrastructure.db.repositories.seguridad.roles import RolRepository
from app.kernel.domain.exceptions import EntityNotFoundException

class DeleteRol:
    def __init__(self, repository: RolRepository):
        self.repository = repository

    async def execute(self, role_id: int) -> None:
        role = await self.repository.get(role_id)
        if not role:
            raise EntityNotFoundException(f"Rol con id '{role_id}' no encontrado.")

        await self.repository.delete(role_id)
