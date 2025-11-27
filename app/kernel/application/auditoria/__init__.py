# app/kernel/application/auditoria/__init__.py

"""
Módulo de Aplicación: Auditoría

Casos de uso para:
- Auditoría de acciones (CRUD, login, etc.)
- Tracking de sesiones activas
- Historial de cambios campo por campo
- Control de exportaciones
- Auditoría de consultas a IA
"""

# Auditoría de Acciones
from .auditoria_acciones import (
    RegistrarAccionCU,
    ListarAccionesCU,
    ObtenerAccionCU,
    BuscarAccionesCU,
    ObtenerEstadisticasCU,
    LimpiarAccionesAntiguasCU,
    RegistrarAccionDTO,
    ListarAccionesPorUsuarioDTO,
    ListarAccionesPorSedeDTO,
    ListarAccionesPorEntidadDTO,
    ListarAccionesPorNivelDTO,
    ListarErroresDTO,
    BuscarPorDescripcionDTO,
    BuscarPorEndpointDTO,
    BuscarPorIPDTO,
    ObtenerEstadisticasDTO,
    ObtenerActividadPorHoraDTO,
    ObtenerUsuariosMasActivosDTO,
    ObtenerErroresPorEndpointDTO,
    LimpiarAccionesAntiguasDTO,
)

# Auditoría de Sesiones
from .auditoria_sesiones import (
    RegistrarInicioSesionCU,
    ActualizarHeartbeatCU,
    CerrarSesionCU,
    ListarSesionesActivasCU,
    ForzarCierreSesionesCU,
    CerrarSesionesInactivasCU,
    RegistrarInicioSesionDTO,
    ActualizarHeartbeatDTO,
    CerrarSesionDTO,
    ListarSesionesActivasDTO,
    ForzarCierreSesionesDTO,
    CerrarSesionesInactivasDTO,
)

# Auditoría de Cambios
from .auditoria_cambios import (
    RegistrarCambioCU,
    RegistrarCambiosMultiplesCU,
    ListarCambiosCU,
    RegistrarCambioDTO,
    RegistrarCambiosMultiplesDTO,
    ListarCambiosPorAccionDTO,
    ObtenerCambioPorCampoDTO,
)

# Auditoría de Exportaciones
from .auditoria_exportaciones import (
    RegistrarExportacionCU,
    MarcarExportacionDescargadaCU,
    ListarExportacionesCU,
    DetectarExportacionesSospechosasCU,
    ObtenerEstadisticasExportacionesCU,
    RegistrarExportacionDTO,
    MarcarExportacionDescargadaDTO,
    ListarExportacionesPorUsuarioDTO,
    ListarExportacionesPorSedeDTO,
    ListarExportacionesPorTipoDTO,
    ListarExportacionesFallidasDTO,
    DetectarExportacionesSospechosasDTO,
    ObtenerEstadisticasExportacionesDTO,
    ObtenerTotalRegistrosExportadosDTO,
)

# Auditoría de Prompts IA
from .auditoria_prompts_ia import (
    RegistrarPromptIACU,
    ListarPromptsIACU,
    CalcularConsumoIACU,
    DetectarPromptsSensiblesCU,
    ObtenerEstadisticasIACU,
    RegistrarPromptIADTO,
    ListarPromptsPorUsuarioDTO,
    ListarPromptsPorSedeDTO,
    ListarPromptsConDatosSensiblesDTO,
    ListarPromptsFallidosDTO,
    CalcularTokensConsumidosDTO,
    CalcularCostoTotalDTO,
    DetectarPromptsSensiblesDTO,
    ObtenerEstadisticasIADTO,
    ObtenerDuracionPromedioDTO,
    ObtenerUsuariosMasActivosIADTO,
)

__all__ = [
    # === AUDITORÍA DE ACCIONES ===
    "RegistrarAccionCU",
    "ListarAccionesCU",
    "ObtenerAccionCU",
    "BuscarAccionesCU",
    "ObtenerEstadisticasCU",
    "LimpiarAccionesAntiguasCU",
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
    
    # === AUDITORÍA DE SESIONES ===
    "RegistrarInicioSesionCU",
    "ActualizarHeartbeatCU",
    "CerrarSesionCU",
    "ListarSesionesActivasCU",
    "ForzarCierreSesionesCU",
    "CerrarSesionesInactivasCU",
    "RegistrarInicioSesionDTO",
    "ActualizarHeartbeatDTO",
    "CerrarSesionDTO",
    "ListarSesionesActivasDTO",
    "ForzarCierreSesionesDTO",
    "CerrarSesionesInactivasDTO",
    
    # === AUDITORÍA DE CAMBIOS ===
    "RegistrarCambioCU",
    "RegistrarCambiosMultiplesCU",
    "ListarCambiosCU",
    "RegistrarCambioDTO",
    "RegistrarCambiosMultiplesDTO",
    "ListarCambiosPorAccionDTO",
    "ObtenerCambioPorCampoDTO",
    
    # === AUDITORÍA DE EXPORTACIONES ===
    "RegistrarExportacionCU",
    "MarcarExportacionDescargadaCU",
    "ListarExportacionesCU",
    "DetectarExportacionesSospechosasCU",
    "ObtenerEstadisticasExportacionesCU",
    "RegistrarExportacionDTO",
    "MarcarExportacionDescargadaDTO",
    "ListarExportacionesPorUsuarioDTO",
    "ListarExportacionesPorSedeDTO",
    "ListarExportacionesPorTipoDTO",
    "ListarExportacionesFallidasDTO",
    "DetectarExportacionesSospechosasDTO",
    "ObtenerEstadisticasExportacionesDTO",
    "ObtenerTotalRegistrosExportadosDTO",
    
    # === AUDITORÍA DE PROMPTS IA ===
    "RegistrarPromptIACU",
    "ListarPromptsIACU",
    "CalcularConsumoIACU",
    "DetectarPromptsSensiblesCU",
    "ObtenerEstadisticasIACU",
    "RegistrarPromptIADTO",
    "ListarPromptsPorUsuarioDTO",
    "ListarPromptsPorSedeDTO",
    "ListarPromptsConDatosSensiblesDTO",
    "ListarPromptsFallidosDTO",
    "CalcularTokensConsumidosDTO",
    "CalcularCostoTotalDTO",
    "DetectarPromptsSensiblesDTO",
    "ObtenerEstadisticasIADTO",
    "ObtenerDuracionPromedioDTO",
    "ObtenerUsuariosMasActivosIADTO",
]
