
from fastapi import APIRouter, Depends, HTTPException, status

from app.interfaces.api.v1.deps import get_uow_dep
from app.kernel.application.inventario.update_familia import UpdateFamilia, UpdateFamiliaRequest
from app.kernel.application.inventario.crear_categoria import CreateCategoria, CreateCategoriaRequest, CategoriaResponse
from app.kernel.application.inventario.get_categorias import GetCategorias, GetCategoriasResponse
from app.kernel.application.inventario.update_categoria import UpdateCategoria, UpdateCategoriaRequest
from app.kernel.application.inventario.delete_categoria import DeleteCategoria
from app.infrastructure.db.repositories.inventario.categorias import CategoriaRepository

# ... (previous imports)

@router.post("/categorias", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    request: CreateCategoriaRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Crea una nueva categoría de items.
    """
    try:
        repository = CategoriaRepository(uow.session_required)
        service = CreateCategoria(repository)
        created_categoria = await service.execute(request)
        return created_categoria
    except DuplicatedEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

@router.get("/categorias", response_model=GetCategoriasResponse)
async def get_categorias(
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Obtiene una lista de todas las categorías de items.
    """
    repository = CategoriaRepository(uow.session_required)
    service = GetCategorias(repository)
    categorias = await service.execute()
    return categorias

@router.put("/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_categoria(
    categoria_id: int,
    request: UpdateCategoriaRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Actualiza una categoría de items existente.
    """
    try:
        repository = CategoriaRepository(uow.session_required)
        service = UpdateCategoria(repository)
        await service.execute(categoria_id, request)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

@router.delete("/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(
    categoria_id: int,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Elimina una categoría de items existente.
    """
    try:
        repository = CategoriaRepository(uow.session_required)
        service = DeleteCategoria(repository)
        await service.execute(categoria_id)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

from app.kernel.domain.exceptions import EntityNotFoundException

# ... (previous imports)

@router.put("/familias/{familia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_familia(
    familia_id: int,
    request: UpdateFamiliaRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Actualiza una familia de items existente.
    """
    try:
        repository = FamiliaRepository(uow.session_required)
        service = UpdateFamilia(repository)
        await service.execute(familia_id, request)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

@router.delete("/familias/{familia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_familia(
    familia_id: int,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Elimina una familia de items existente.
    """
    try:
        repository = FamiliaRepository(uow.session_required)
        service = DeleteFamilia(repository)
        await service.execute(familia_id)
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ... (previous imports)

@router.get("/familias", response_model=GetFamiliasResponse)
async def get_familias(
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Obtiene una lista de todas las familias de items.
    """
    repository = FamiliaRepository(uow.session_required)
    service = GetFamilias(repository)
    familias = await service.execute()
    return familias
from app.kernel.domain.exceptions import DuplicatedEntityException
from app.infrastructure.db.uow import UnitOfWork
from app.infrastructure.db.repositories.inventario.familias import FamiliaRepository

router = APIRouter(prefix="/inventario", tags=["Inventario"])

@router.post("/familias", response_model=FamiliaResponse, status_code=status.HTTP_201_CREATED)
async def create_familia(
    request: CreateFamiliaRequest,
    uow: UnitOfWork = Depends(get_uow_dep),
):
    """
    Crea una nueva familia de items.
    """
    try:
        repository = FamiliaRepository(uow.session_required)
        service = CreateFamilia(repository)
        created_familia = await service.execute(request)
        return created_familia
    except DuplicatedEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
