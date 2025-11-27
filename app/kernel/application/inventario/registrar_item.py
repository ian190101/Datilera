# app/kernel/application/inventario/registrar_item.py
from __future__ import annotations

import re
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.infrastructure.db.repositories.inventario.items_repo import ItemsRepository
from app.infrastructure.db.repositories.inventario.items_atributos_repo import ItemsAtributosRepository
from app.infrastructure.db.models.inventario import Item as ItemModel
from app.infrastructure.db.models.inventario import ItemAtributo as ItemAtributoModel
from app.kernel.domain.common.excepciones import AlreadyExistsError

def _slug(texto: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", texto.strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)

def _generar_sku(nombre: str, attrs: list[tuple[str, str]], prefijo: Optional[str] = None, maxlen: int = 50) -> str:
    partes = []
    if prefijo:
        partes.append(_slug(prefijo))
    partes.append(_slug(nombre))
    for k, v in attrs:
        if k.lower() in {"color", "talla", "marca"}:
            partes.append(_slug(v))
    sku = "-".join(partes)[:maxlen]
    return sku or _slug(nombre)[:maxlen]

class RegistrarItemAtributo(BaseModel):
    nombre: str = Field(..., max_length=60)
    valor: str = Field(..., max_length=120)

class RegistrarItemRequest(BaseModel):
    categoria_id: int
    nombre: str = Field(..., max_length=120)
    precio_unitario: Decimal
    unidad_medida: str = Field("unidad", max_length=20)
    descripcion: Optional[str] = None
    atributos: List[RegistrarItemAtributo] = Field(default_factory=list)
    prefijo_sku: Optional[str] = None

    @field_validator("atributos")
    @classmethod
    def validar_atributos(cls, v):
        nombres = [a.nombre.strip().lower() for a in v]
        if len(nombres) != len(set(nombres)):
            raise ValueError("Atributos duplicados por nombre.")
        return v

class ItemCompletoResponse(BaseModel):
    id: int
    categoria_id: int
    codigo: str
    nombre: str
    descripcion: Optional[str]
    precio_unitario: Decimal
    unidad_medida: str
    activo: bool
    atributos: List[RegistrarItemAtributo]

class RegistrarItem:
    """
    Registra un ítem generando SKU a partir del nombre y atributos (color/talla/marca) y persiste los atributos.
    """
    def __init__(self, items_repo: ItemsRepository, attrs_repo: ItemsAtributosRepository):
        self.items_repo = items_repo
        self.attrs_repo = attrs_repo

    async def execute(self, req: RegistrarItemRequest) -> ItemCompletoResponse:
        pares = [(a.nombre, a.valor) for a in req.atributos]
        sku = _generar_sku(req.nombre, pares, prefijo=req.prefijo_sku, maxlen=50)

        if await self.items_repo.one(where=ItemModel.codigo == sku):
            raise AlreadyExistsError(f"El código/SKU '{sku}' ya existe.")

        item = await self.items_repo.create(ItemModel(
            categoria_id=req.categoria_id,
            codigo=sku,
            nombre=req.nombre,
            descripcion=req.descripcion,
            precio_unitario=req.precio_unitario,
            unidad_medida=req.unidad_medida,
        ))

        for a in req.atributos:
            await self.attrs_repo.create(ItemAtributoModel(
                item_id=item.id,
                nombre_atributo=a.nombre,
                valor_atributo=a.valor,
            ))

        return ItemCompletoResponse(
            id=item.id,
            categoria_id=item.categoria_id,
            codigo=item.codigo,
            nombre=item.nombre,
            descripcion=item.descripcion,
            precio_unitario=item.precio_unitario,
            unidad_medida=item.unidad_medida,
            activo=item.activo,
            atributos=req.atributos,
        )
