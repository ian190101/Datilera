# app/kernel/application/auditoria/auditoria_exportaciones/__init__.py

"""
Casos de Uso: Auditoría de Exportaciones
"""

from .registrar_exportacion import RegistrarExportacionCU, RegistrarExportacionDTO
from .marcar_exportacion_descargada import (
    MarcarExportacionDescargadaCU,
    MarcarExportacionDescargadaDTO,
)
from .listar_exportaciones import (
    ListarExportacionesCU,
    ListarExportacionesPorUsuarioDTO,
    ListarExportacionesPorSedeDTO,
    ListarExportacionesPorTipoDTO,
    ListarExportacionesFallidasDTO,
)
from .detectar_exportaciones_sospechosas import (
    DetectarExportacionesSospechosasCU,
    DetectarExportacionesSospechosasDTO,
)
from .obtener_estadisticas_exportaciones import (
    ObtenerEstadisticasExportacionesCU,
    ObtenerEstadisticasExportacionesDTO,
    ObtenerTotalRegistrosExportadosDTO,
)

__all__ = [
    # Casos de Uso
    "RegistrarExportacionCU",
    "MarcarExportacionDescargadaCU",
    "ListarExportacionesCU",
    "DetectarExportacionesSospechosasCU",
    "ObtenerEstadisticasExportacionesCU",
    # DTOs
    "RegistrarExportacionDTO",
    "MarcarExportacionDescargadaDTO",
    "ListarExportacionesPorUsuarioDTO",
    "ListarExportacionesPorSedeDTO",
    "ListarExportacionesPorTipoDTO",
    "ListarExportacionesFallidasDTO",
    "DetectarExportacionesSospechosasDTO",
    "ObtenerEstadisticasExportacionesDTO",
    "ObtenerTotalRegistrosExportadosDTO",
]
