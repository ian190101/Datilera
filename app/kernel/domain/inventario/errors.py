from __future__ import annotations
from app.kernel.domain.common.excepciones import BaseDominioError

class FamiliaNoEncontrada(BaseDominioError):
    status_code = 404
    code = "FAMILIA_NOT_FOUND"

class CategoriaNoEncontrada(BaseDominioError):
    status_code = 404
    code = "CATEGORIA_NOT_FOUND"

class ItemNoEncontrado(BaseDominioError):
    status_code = 404
    code = "ITEM_NOT_FOUND"

class CodigoItemDuplicado(BaseDominioError):
    status_code = 409
    code = "ITEM_CODE_DUPLICATED"

class CategoriaDuplicada(BaseDominioError):
    status_code = 409
    code = "CATEGORY_DUPLICATED"

class StockInsuficiente(BaseDominioError):
    status_code = 409
    code = "INSUFFICIENT_STOCK"

class MovimientoNoSoportado(BaseDominioError):
    status_code = 422
    code = "UNSUPPORTED_MOVEMENT"

class PrestamoNoEncontrado(BaseDominioError):
    status_code = 404
    code = "PRESTAMO_NOT_FOUND"

class PrestamoYaDevuelto(BaseDominioError):
    status_code = 409
    code = "PRESTAMO_ALREADY_RETURNED"
    
