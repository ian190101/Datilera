# app/kernel/domain/auditoria/__init__.py

"""
Módulo de Dominio: Auditoría

Incluye:
- Auditoría de acciones (CRUD, login, etc.)
- Tracking de sesiones activas
- Historial de cambios campo por campo
- Control de exportaciones
- Auditoría de consultas a IA
"""

# Entidades
from .auditoria_accion_entidad import AuditoriaAccion
from .auditoria_sesion_entidad import AuditoriaSesion
from .auditoria_cambio_entidad import AuditoriaCambio
from .auditoria_exportacion_entidad import AuditoriaExportacion
from .auditoria_prompt_ia_entidad import AuditoriaPromptIA

# Ports
from .ports import (
    AuditoriaAccionRepositoryPort,
    AuditoriaSesionRepositoryPort,
    AuditoriaCambioRepositoryPort,
    AuditoriaExportacionRepositoryPort,
    AuditoriaPromptIARepositoryPort,
)

# Errors
from .errors import (
    # Base
    AuditoriaError,
    # Acciones
    AccionAuditoriaNoEncontrada,
    NivelAuditoriaInvalido,
    EntidadAuditoriaInvalida,
    AccionAuditoriaInvalida,
    # Sesiones
    SesionAuditoriaNoEncontrada,
    SesionYaCerrada,
    SesionInactiva,
    DispositivoTipoInvalido,
    RazonCierreInvalida,
    # Cambios
    CambioAuditoriaNoEncontrado,
    TipoDatoInvalido,
    CampoSinCambios,
    # Exportaciones
    ExportacionAuditoriaNoEncontrada,
    TipoExportacionInvalido,
    FormatoExportacionInvalido,
    ExportacionMasivaSospechosa,
    ExportacionYaDescargada,
    # Prompts IA
    PromptIAAuditoriaNoEncontrado,
    CategoriaIAInvalida,
    PromptConDatosSensibles,
    LimiteTokensExcedido,
    CostoIAExcesivo,
    ModeloIANoDisponible,
    # Validación
    CodigoRespuestaInvalido,
    MetodoHTTPInvalido,
    DuracionNegativa,
)

__all__ = [
    # Entidades
    "AuditoriaAccion",
    "AuditoriaSesion",
    "AuditoriaCambio",
    "AuditoriaExportacion",
    "AuditoriaPromptIA",
    # Ports
    "AuditoriaAccionRepositoryPort",
    "AuditoriaSesionRepositoryPort",
    "AuditoriaCambioRepositoryPort",
    "AuditoriaExportacionRepositoryPort",
    "AuditoriaPromptIARepositoryPort",
    # Errors
    "AuditoriaError",
    "AccionAuditoriaNoEncontrada",
    "NivelAuditoriaInvalido",
    "EntidadAuditoriaInvalida",
    "AccionAuditoriaInvalida",
    "SesionAuditoriaNoEncontrada",
    "SesionYaCerrada",
    "SesionInactiva",
    "DispositivoTipoInvalido",
    "RazonCierreInvalida",
    "CambioAuditoriaNoEncontrado",
    "TipoDatoInvalido",
    "CampoSinCambios",
    "ExportacionAuditoriaNoEncontrada",
    "TipoExportacionInvalido",
    "FormatoExportacionInvalido",
    "ExportacionMasivaSospechosa",
    "ExportacionYaDescargada",
    "PromptIAAuditoriaNoEncontrado",
    "CategoriaIAInvalida",
    "PromptConDatosSensibles",
    "LimiteTokensExcedido",
    "CostoIAExcesivo",
    "ModeloIANoDisponible",
    "CodigoRespuestaInvalido",
    "MetodoHTTPInvalido",
    "DuracionNegativa",
]
