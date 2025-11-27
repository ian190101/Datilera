# app/kernel/application/ia/probar_conexion.py

from __future__ import annotations
from typing import List, Dict, Any
from pydantic import BaseModel

from app.kernel.domain.ia import IAProviderPort, ProveedorIANoDisponible


class ProbarConexionIAResponse(BaseModel):
    estados: List[Dict[str, Any]]


class ProbarConexionIACU:
    """
    Caso de Uso: Probar conexión a proveedores IA.
    """

    def __init__(self, providers: list[IAProviderPort]):
        self.providers = providers

    async def ejecutar(self) -> ProbarConexionIAResponse:
        resultados: List[Dict[str, Any]] = []
        for provider in self.providers:
            nombre = provider.get_nombre_proveedor()
            try:
                ok = await provider.validar_conexion()
                resultados.append(
                    {
                        "proveedor": nombre,
                        "disponible": bool(ok),
                    }
                )
            except Exception as e:
                resultados.append(
                    {
                        "proveedor": nombre,
                        "disponible": False,
                        "error": str(e),
                    }
                )
        return ProbarConexionIAResponse(estados=resultados)
