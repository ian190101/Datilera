# app/kernel/application/inventario/__init__.py

# Familias
from .crear_familia import CreateFamilia, CreateFamiliaRequest, FamiliaResponse
from .get_familias import GetFamilias, GetFamiliasResponse
from .update_familia import UpdateFamilia, UpdateFamiliaRequest
from .delete_familia import DeleteFamilia

# Categorías
from .crear_categoria import CreateCategoria, CreateCategoriaRequest, CategoriaResponse
from .get_categorias import GetCategorias, GetCategoriasResponse
from .update_categoria import UpdateCategoria, UpdateCategoriaRequest
from .delete_categoria import DeleteCategoria

# Ítems (básico)
from .crear_item import CreateItem, CreateItemRequest, ItemResponse
from .get_items import GetItems, GetItemsResponse

# Stock y Alertas (Sprint 2)
from .mover_stock import MoverStock, MoverStockRequest, MovimientoResponse
from .generar_alertas import GenerarAlertasStock, GenerarAlertasVencimiento, GenerarAlertasResponse

# Registro avanzado de ítems (SKU + atributos)
from .registrar_item import RegistrarItem, RegistrarItemRequest, ItemCompletoResponse
from .registrar_prestamo import RegistrarPrestamo, RegistrarPrestamoRequest, PrestamoResponse
from .devolver_prestamo import DevolverPrestamo, DevolverPrestamoRequest

__all__ = [
    # Familias
    "CreateFamilia", "CreateFamiliaRequest", "FamiliaResponse",
    "GetFamilias", "GetFamiliasResponse",
    "UpdateFamilia", "UpdateFamiliaRequest",
    "DeleteFamilia",

    # Categorías
    "CreateCategoria", "CreateCategoriaRequest", "CategoriaResponse",
    "GetCategorias", "GetCategoriasResponse",
    "UpdateCategoria", "UpdateCategoriaRequest",
    "DeleteCategoria",

    # Ítems (básico)
    "CreateItem", "CreateItemRequest", "ItemResponse",
    "GetItems", "GetItemsResponse",

    # Stock y Alertas
    "MoverStock", "MoverStockRequest", "MovimientoResponse",
    "GenerarAlertasStock", "GenerarAlertasVencimiento", "GenerarAlertasResponse",

    # Registro avanzado
    "RegistrarItem", "RegistrarItemRequest", "ItemCompletoResponse",

    #Prestamos
    "RegistrarPrestamo", "RegistrarPrestamoRequest", "PrestamoResponse",
    "DevolverPrestamo", "DevolverPrestamoRequest",

]
