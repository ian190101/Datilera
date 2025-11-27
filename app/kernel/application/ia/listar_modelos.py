# app/kernel/application/ia/listar_modelos.py

from __future__ import annotations
from typing import List, Dict, Any
from pydantic import BaseModel

from app.kernel.domain.ia import IAProviderPort


class ListarProveedoresModelosResponse(BaseModel):
    proveedores: List[Dict[str, Any]]


class ListarModelosCU:
    """
    Caso de Uso: Listar proveedores y modelos IA disponibles.
    """

    def __init__(self, providers: list[IAProviderPort]):
        self.providers = providers

    async def ejecutar(self) -> ListarProveedoresModelosResponse:
        data: List[Dict[str, Any]] = []
        for provider in self.providers:
            data.append(
                {
                    "proveedor": provider.get_nombre_proveedor(),
                    "modelos": provider.get_modelos_disponibles(),
                }
            )
        return ListarProveedoresModelosResponse(proveedores=data)
