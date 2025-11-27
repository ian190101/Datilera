# app/infrastructure/services/ia/__init__.py

"""
Servicios de IA (MCP) a nivel de infraestructura.

Este módulo expone funciones para obtener proveedores IA concretos,
pero el dominio solo depende de la interfaz IAProviderPort.
"""

from __future__ import annotations
from typing import List, Optional

from app.kernel.domain.ia import IAProviderPort


# Por ahora, lista vacía; luego agregarás implementaciones concretas:
# from .providers.openai_provider import OpenAIProvider
# from .providers.perplexity_provider import PerplexityProvider
# etc.


def get_ia_providers() -> List[IAProviderPort]:
    """
    Retorna la lista de proveedores IA disponibles.
    Inicialmente vacío; se irán agregando implementaciones concretas.
    """
    providers: List[IAProviderPort] = []

    # Ejemplo futuro:
    # providers.append(OpenAIProvider())
    # providers.append(PerplexityProvider())
    # providers.append(GeminiProvider())
    # providers.append(GrokProvider())

    return providers


def get_ia_provider_by_name(nombre: str) -> Optional[IAProviderPort]:
    """
    Retorna un proveedor por nombre (case-insensitive) o None si no existe.
    """
    nombre = nombre.lower()
    for provider in get_ia_providers():
        if provider.get_nombre_proveedor().lower() == nombre:
            return provider
    return None
