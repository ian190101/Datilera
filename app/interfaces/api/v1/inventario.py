# app/interfaces/api/v1/inventario.py
from __future__ import annotations
from fastapi import APIRouter, Depends, status
from typing import Annotated

from app.infrastructure.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

# Repositorios (en plural)
from app.infrastructure.db.repositories.inventario.familias_repo import FamiliasRepository
from app.infrastructure.db.repositories.inventario.categorias_repo import CategoriasRepository
from app.infrastructure.db.repositories.inventario.items_repo import ItemsRepository
from app.infrastructure.db.repositories.inventario.items_atributos_repo import ItemsAtributosRepository
from app.infrastructure.db.repositories.inventario.stock_sede_repo import StockSedeRepository
from app.infrastructure.db.repositories.inventario.movimientos_stock_repo import MovimientosStockRepository
from app.infrastructure.db.repositories.inventario.alertas_stock_repo import AlertasStockRepository
from app.infrastructure.db.repositories.inventario.alertas_vencimiento_repo import AlertasVencimientoRepository
from app.infrastructure.db.repositories.inventario.prestamos_uniformes_repo import PrestamosUniformesRepository



# Casos de uso
from app.kernel.application.inventario import (
    # Familias
    CreateFamilia, CreateFamiliaRequest, FamiliaResponse,
    GetFamilias, GetFamiliasResponse,
    UpdateFamilia, UpdateFamiliaRequest,
    DeleteFamilia,
    # Categorías
    CreateCategoria, CreateCategoriaRequest, CategoriaResponse,
    GetCategorias, GetCategoriasResponse,
    UpdateCategoria, UpdateCategoriaRequest,
    DeleteCategoria,
    # Ítems
    CreateItem, CreateItemRequest, ItemResponse,
    GetItems, GetItemsResponse,
    # Stock y Movimientos
    MoverStock, MoverStockRequest, MovimientoResponse, 
    # Alertas
    GenerarAlertasStock, GenerarAlertasVencimiento, GenerarAlertasResponse,
    # Registro avanzado
    RegistrarItem, RegistrarItemRequest, ItemCompletoResponse,
)

from app.kernel.application.inventario.get_stock_por_sede import GetStockPorSede
from app.kernel.application.inventario.get_movimientos_por_item import GetMovimientosPorItem
from app.kernel.application.inventario import (
    RegistrarPrestamo, RegistrarPrestamoRequest, PrestamoResponse,
    DevolverPrestamo, DevolverPrestamoRequest,
)

router = APIRouter(prefix="/inventario", tags=["Inventario"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Helpers de DI por request
def fam_repo(db: AsyncSession) -> FamiliasRepository: return FamiliasRepository(db)
def cat_repo(db: AsyncSession) -> CategoriasRepository: return CategoriasRepository(db)
def itm_repo(db: AsyncSession) -> ItemsRepository: return ItemsRepository(db)
def attrs_repo(db: AsyncSession) -> ItemsAtributosRepository: return ItemsAtributosRepository(db)
def stk_repo(db: AsyncSession) -> StockSedeRepository: return StockSedeRepository(db)
def mov_repo(db: AsyncSession) -> MovimientosStockRepository: return MovimientosStockRepository(db)
def ast_repo(db: AsyncSession) -> AlertasStockRepository: return AlertasStockRepository(db)
def av_repo(db: AsyncSession) -> AlertasVencimientoRepository: return AlertasVencimientoRepository(db)

# Familias
@router.post("/familias", response_model=FamiliaResponse, status_code=status.HTTP_201_CREATED)
async def crear_familia(payload: CreateFamiliaRequest, db: SessionDep):
    uc = CreateFamilia(fam_repo(db))
    return await uc.execute(payload)

@router.get("/familias", response_model=GetFamiliasResponse)
async def listar_familias(db: SessionDep):
    uc = GetFamilias(fam_repo(db))
    return await uc.execute()

@router.put("/familias/{familia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_familia(familia_id: int, payload: UpdateFamiliaRequest, db: SessionDep):
    uc = UpdateFamilia(fam_repo(db))
    await uc.execute(familia_id, payload)
    return None

@router.delete("/familias/{familia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_familia(familia_id: int, db: SessionDep):
    uc = DeleteFamilia(fam_repo(db))
    await uc.execute(familia_id)
    return None

# Categorías
@router.post("/categorias", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def crear_categoria(payload: CreateCategoriaRequest, db: SessionDep):
    uc = CreateCategoria(cat_repo(db))
    return await uc.execute(payload)

@router.get("/categorias", response_model=GetCategoriasResponse)
async def listar_categorias(db: SessionDep):
    uc = GetCategorias(cat_repo(db))
    return await uc.execute()

@router.put("/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def actualizar_categoria(categoria_id: int, payload: UpdateCategoriaRequest, db: SessionDep):
    uc = UpdateCategoria(cat_repo(db))
    await uc.execute(categoria_id, payload)
    return None

@router.delete("/categorias/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria(categoria_id: int, db: SessionDep):
    uc = DeleteCategoria(cat_repo(db))
    await uc.execute(categoria_id)
    return None

# Ítems
@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def crear_item(payload: CreateItemRequest, db: SessionDep):
    uc = CreateItem(itm_repo(db))
    return await uc.execute(payload)

@router.get("/items", response_model=GetItemsResponse)
async def listar_items(db: SessionDep):
    uc = GetItems(itm_repo(db))
    return await uc.execute()

# Registro avanzado (SKU + atributos)
@router.post("/items/registrar", response_model=ItemCompletoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_item(payload: RegistrarItemRequest, db: SessionDep):
    uc = RegistrarItem(itm_repo(db), attrs_repo(db))
    return await uc.execute(payload)

# Stock por sede y movimientos
@router.post("/movimientos", response_model=list[MovimientoResponse], status_code=status.HTTP_201_CREATED)
async def mover_stock(payload: MoverStockRequest, db: SessionDep):
    uc = MoverStock(stk_repo(db), mov_repo(db))
    return await uc.execute(payload)

# Alertas
@router.post("/alertas/stock/generar", response_model=GenerarAlertasResponse)
async def generar_alertas_stock(db: SessionDep):
    uc = GenerarAlertasStock(stk_repo(db), ast_repo(db))
    return await uc.execute()

@router.post("/alertas/vencimiento/contar", response_model=GenerarAlertasResponse)
async def contar_alertas_vencimientos(db: SessionDep):
    uc = GenerarAlertasVencimiento(av_repo(db))
    return await uc.execute()

@router.put("/stock/{item_id}/minimo/{sede_id}")
async def ajustar_minimo(item_id: int, sede_id: int, minimo: float, db: SessionDep):
    from app.kernel.application.inventario.ajustar_stock_minimo import AjustarStockMinimo
    uc = AjustarStockMinimo(StockSedeRepository(db))
    await uc.execute(item_id, sede_id, minimo)
    return {"ok": True}

@router.get("/stock/sede/{sede_id}")
async def stock_por_sede(sede_id: int, db: SessionDep):
    uc = GetStockPorSede(StockSedeRepository(db))
    return [dto.model_dump() for dto in await uc.execute(sede_id)]

@router.get("/movimientos/item/{item_id}", response_model=list[MovimientoResponse])
async def movimientos_por_item(item_id: int, db: SessionDep):
    uc = GetMovimientosPorItem(MovimientosStockRepository(db))
    return [m.model_dump() for m in await uc.execute(item_id)]

@router.post("/prestamos", response_model=PrestamoResponse, status_code=201)
async def crear_prestamo(payload: RegistrarPrestamoRequest, db: SessionDep):
    uc = RegistrarPrestamo(PrestamosUniformesRepository(db))
    return await uc.execute(payload)

@router.put("/prestamos/{prestamo_id}/devolver", status_code=204)
async def devolver_prestamo(prestamo_id: int, payload: DevolverPrestamoRequest, db: SessionDep):
    uc = DevolverPrestamo(PrestamosUniformesRepository(db))
    await uc.execute(prestamo_id, payload)
    return None