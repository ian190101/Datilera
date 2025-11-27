# app/kernel/domain/ia/__init__.py

"""
Módulo de Dominio: IA

Gestión de consultas a proveedores de IA con MCP estándar.
"""

# Entidades
from .ia_consulta_entidad import IAConsulta

# Ports
from .ports import IAConsultasRepositoryPort, IAProviderPort

# Errors
from .errors import (
    IAError,
    ConsultaIANoEncontrada,
    ProveedorIANoDisponible,
    ModeloIANoDisponible,
    ErrorConsultaIA,
    LimiteTokensExcedido,
    CostoExcesivo,
    PromptConDatosSensibles,
    ConfiguracionIAInvalida,
    APIKeyNoConfigurada,
    RateLimitExcedido,
)

__all__ = [
    # Entidades
    "IAConsulta",
    
    # Ports
    "IAConsultasRepositoryPort",
    "IAProviderPort",
    
    # Errors
    "IAError",
    "ConsultaIANoEncontrada",
    "ProveedorIANoDisponible",
    "ModeloIANoDisponible",
    "ErrorConsultaIA",
    "LimiteTokensExcedido",
    "CostoExcesivo",
    "PromptConDatosSensibles",
    "ConfiguracionIAInvalida",
    "APIKeyNoConfigurada",
    "RateLimitExcedido",
]
