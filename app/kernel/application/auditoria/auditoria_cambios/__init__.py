# app/kernel/application/auditoria/auditoria_cambios/__init__.py

"""
Casos de Uso: Auditoría de Cambios
"""

from .registrar_cambio import RegistrarCambioCU, RegistrarCambioDTO
from .registrar_cambios_multiples import RegistrarCambiosMultiplesCU, RegistrarCambiosMultiplesDTO
from .listar_cambios import (
    ListarCambiosCU,
    ListarCambiosPorAccionDTO,
    ObtenerCambioPorCampoDTO,
)

__all__ = [
    # Casos de Uso
    "RegistrarCambioCU",
    "RegistrarCambiosMultiplesCU",
    "ListarCambiosCU",
    # DTOs
    "RegistrarCambioDTO",
    "RegistrarCambiosMultiplesDTO",
    "ListarCambiosPorAccionDTO",
    "ObtenerCambioPorCampoDTO",
]
