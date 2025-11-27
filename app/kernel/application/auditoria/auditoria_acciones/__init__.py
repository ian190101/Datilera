# app/kernel/application/auditoria/auditoria_acciones/__init__.py

"""
Casos de Uso: Auditoría de Acciones
"""

from .registrar_accion import RegistrarAccionCU, RegistrarAccionDTO
from .listar_acciones import (
    ListarAccionesCU,
    ListarAccionesPorUsuarioDTO,
    ListarAccionesPorSedeDTO,
    ListarAccionesPorEntidadDTO,
    ListarAccionesPorNivelDTO,
    ListarErroresDTO,
)
from .obtener_accion import ObtenerAccionCU
from .buscar_acciones import (
    BuscarAccionesCU,
    BuscarPorDescripcionDTO,
    BuscarPorEndpointDTO,
    BuscarPorIPDTO,
)
from .obtener_estadistica import (
    ObtenerEstadisticasCU,
    ObtenerEstadisticasDTO,
    ObtenerActividadPorHoraDTO,
    ObtenerUsuariosMasActivosDTO,
    ObtenerErroresPorEndpointDTO,
)
from .limpiar_acciones_antiguas import LimpiarAccionesAntiguasCU, LimpiarAccionesAntiguasDTO

__all__ = [
    # Casos de Uso
    "RegistrarAccionCU",
    "ListarAccionesCU",
    "ObtenerAccionCU",
    "BuscarAccionesCU",
    "ObtenerEstadisticasCU",
    "LimpiarAccionesAntiguasCU",
    # DTOs
    "RegistrarAccionDTO",
    "ListarAccionesPorUsuarioDTO",
    "ListarAccionesPorSedeDTO",
    "ListarAccionesPorEntidadDTO",
    "ListarAccionesPorNivelDTO",
    "ListarErroresDTO",
    "BuscarPorDescripcionDTO",
    "BuscarPorEndpointDTO",
    "BuscarPorIPDTO",
    "ObtenerEstadisticasDTO",
    "ObtenerActividadPorHoraDTO",
    "ObtenerUsuariosMasActivosDTO",
    "ObtenerErroresPorEndpointDTO",
    "LimpiarAccionesAntiguasDTO",
]
