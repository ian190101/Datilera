from __future__ import annotations
from typing import List, Optional

from app.kernel.domain.ia.ia import IAProviderPort
# Importamos la implementación concreta
from .providers.gemini_provider import GeminiProvider 

# Singleton cache para no instanciar múltiples veces
_providers_cache: List[IAProviderPort] = []

def get_ia_providers() -> List[IAProviderPort]:
    """
    Retorna la lista de proveedores IA disponibles.
    """
    global _providers_cache
    
    if not _providers_cache:
        # Aquí registras tus proveedores disponibles
        try:
            _providers_cache.append(GeminiProvider())
            # _providers_cache.append(OpenAIProvider()) # Futuro
        except Exception as e:
            print(f"Error inicializando proveedores IA: {e}")

    return _providers_cache


def get_ia_provider_by_name(nombre: str) -> Optional[IAProviderPort]:
    """
    Retorna un proveedor por nombre (case-insensitive) o el primero por defecto.
    """
    providers = get_ia_providers()
    if not providers:
        return None
        
    nombre = nombre.lower()
    
    # Búsqueda específica
    for provider in providers:
        if provider.get_nombre_proveedor().lower() == nombre:
            return provider
    
    # Fallback: Retornar el primero si no se encuentra el solicitado (opcional)
    # return providers[0] 
    return None