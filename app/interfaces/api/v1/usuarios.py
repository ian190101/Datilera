
from fastapi import APIRouter, Depends, HTTPException, status

from app.interfaces.api.v1.deps import get_uow_dep
from app.kernel.application.seguridad.asignar_rol_usuario import (
    AssignRoleToUser,
    AssignRoleToUserRequest,
)
from app.kernel.domain.exceptions import EntityNotFoundException, DuplicatedEntityException
from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.db.repositories.seguridad.usuarios import UsuarioRepository
from app.infrastructure.db.repositories.seguridad.roles import RolRepository
from app.infrastructure.db.repositories.seguridad.usuarios_roles import UsuarioRolRepository

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

from pydantic import BaseModel

class AssignRoleRequest(BaseModel):
    role_id: int

@router.post("/{user_id}/roles", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role_to_user(
    user_id: int,
    request: AssignRoleRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Asigna un rol a un usuario.
    """
    try:
        user_repo = UsuarioRepository(uow.session_required)
        role_repo = RolRepository(uow.session_required)
        user_role_repo = UsuarioRolRepository(uow.session_required)

        service = AssignRoleToUser(user_repo, role_repo, user_role_repo)
        await service.execute(AssignRoleToUserRequest(user_id=user_id, role_id=request.role_id))
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DuplicatedEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
