
from fastapi import APIRouter, Depends, HTTPException, status

from app.interfaces.api.v1.deps import get_uow_dep
from app.kernel.application.seguridad.update_rol import UpdateRol, UpdateRoleRequest
from app.kernel.application.seguridad.asignar_permiso_rol import AssignPermissionToRole, AssignPermissionToRoleRequest
from app.infrastructure.db.repositories.seguridad.permisos import PermisoRepository
from app.infrastructure.db.repositories.seguridad.roles_permisos import RolPermisoRepository

# ... (previous imports)

from pydantic import BaseModel

class AssignPermissionRequest(BaseModel):
    permission_id: int

@router.post("/{role_id}/permisos", status_code=status.HTTP_204_NO_CONTENT)
async def assign_permission_to_role(
    role_id: int,
    request: AssignPermissionRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Asigna un permiso a un rol.
    """
    try:
        role_repo = RolRepository(uow.session_required)
        permission_repo = PermisoRepository(uow.session_required)
        role_permission_repo = RolPermisoRepository(uow.session_required)

        service = AssignPermissionToRole(role_repo, permission_repo, role_permission_repo)
        await service.execute(AssignPermissionToRoleRequest(role_id=role_id, permission_id=request.permission_id))
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

from app.kernel.domain.exceptions import EntityNotFoundException

# ... (previous imports)

@router.put("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_role(
    role_id: int,
    request: UpdateRoleRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Actualiza un rol existente.
    """
    try:
        repository = RolRepository(uow.session_required)
        service = UpdateRol(repository)
        await service.execute(role_id, request)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Elimina un rol existente.
    """
    try:
        repository = RolRepository(uow.session_required)
        service = DeleteRol(repository)
        await service.execute(role_id)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ... (previous imports)

@router.get("/", response_model=GetRolesResponse)
async def get_roles(
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Obtiene una lista de todos los roles en el sistema.
    """
    repository = RolRepository(uow.session_required)
    service = GetRoles(repository)
    roles = await service.execute()
    return roles
from app.kernel.domain.exceptions import DuplicatedEntityException
from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.db.repositories.seguridad.roles import RolRepository

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    request: CreateRoleRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Crea un nuevo rol en el sistema.
    """
    try:
        repository = RolRepository(uow.session_required)
        service = CrearRol(repository)
        created_role = await service.execute(request)
        return created_role
    except DuplicatedEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
