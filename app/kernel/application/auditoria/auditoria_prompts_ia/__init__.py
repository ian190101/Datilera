# app/kernel/application/auditoria/auditoria_prompts_ia/__init__.py

"""
Casos de Uso: Auditoría de Prompts IA
"""

from .registrar_prompt_ia import RegistrarPromptIACU, RegistrarPromptIADTO
from .listar_prompts_ia import (
    ListarPromptsIACU,
    ListarPromptsPorUsuarioDTO,
    ListarPromptsPorSedeDTO,
    ListarPromptsConDatosSensiblesDTO,
    ListarPromptsFallidosDTO,
)
from .calcular_consumo_ia import (
    CalcularConsumoIACU,
    CalcularTokensConsumidosDTO,
    CalcularCostoTotalDTO,
)
from .detectar_prompts_sensibles import (
    DetectarPromptsSensiblesCU,
    DetectarPromptsSensiblesDTO,
)
from .obtener_estadisticas_ia import (
    ObtenerEstadisticasIACU,
    ObtenerEstadisticasIADTO,
    ObtenerDuracionPromedioDTO,
    ObtenerUsuariosMasActivosIADTO,
)

__all__ = [
    # Casos de Uso
    "RegistrarPromptIACU",
    "ListarPromptsIACU",
    "CalcularConsumoIACU",
    "DetectarPromptsSensiblesCU",
    "ObtenerEstadisticasIACU",
    # DTOs
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
