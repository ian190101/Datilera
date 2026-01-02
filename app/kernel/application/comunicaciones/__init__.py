# app/kernel/application/comunicaciones/__init__.py

"""
Casos de uso (Application Layer) para Comunicaciones.

Organización por funcionalidad:
- conversaciones/: Gestión de conversaciones y participantes
- mensajes/: Envío, lectura y adjuntos de mensajes
- notificaciones/: Creación, lectura y envío de notificaciones
- estadisticas/: Reportes y métricas de comunicaciones
"""

# Conversaciones
from .conversaciones import (
    CrearConversacionUseCase,
    ObtenerConversacionUseCase,
    ListarConversacionesUseCase,
    CerrarConversacionUseCase,
    ReabrirConversacionUseCase,
    AgregarParticipanteUseCase,
    RemoverParticipanteUseCase,
    BuscarConversacionesUseCase,
)

# Mensajes
from .mensajes import (
    EnviarMensajeUseCase,
    ObtenerMensajeUseCase,
    ListarMensajesUseCase,
    MarcarMensajeLeidoUseCase,
    ContarNoLeidosUseCase,
    BuscarMensajesUseCase,
    SubirAdjuntoUseCase,
    ListarAdjuntosUseCase,
    EliminarAdjuntoUseCase,
)

# Notificaciones
from .notificaciones import (
    CrearNotificacionUseCase,
    ObtenerNotificacionUseCase,
    ListarNotificacionesUseCase,
    MarcarNotificacionLeidaUseCase,
    MarcarTodasLeidasUseCase,
    ContarNoLeidasUseCase,
    CrearNotificacionProgramadaUseCase,
    CancelarNotificacionProgramadaUseCase,
    ProcesarNotificacionesProgramadasUseCase,
    ListarTiposNotificacionesUseCase,
    AgruparNotificacionesPorTipoUseCase,
    EnviarNotificacionMasivaUseCase
)

# Estadísticas
from .estadisticas import (
    ObtenerEstadisticasUsuarioUseCase,
    ObtenerEstadisticasSedeUseCase,
)

__all__ = [
    # Conversaciones (8)
    "CrearConversacionUseCase",
    "ObtenerConversacionUseCase",
    "ListarConversacionesUseCase",
    "CerrarConversacionUseCase",
    "ReabrirConversacionUseCase",
    "AgregarParticipanteUseCase",
    "RemoverParticipanteUseCase",
    "BuscarConversacionesUseCase",
    # Mensajes (9)
    "EnviarMensajeUseCase",
    "ObtenerMensajeUseCase",
    "ListarMensajesUseCase",
    "MarcarMensajeLeidoUseCase",
    "ContarNoLeidosUseCase",
    "BuscarMensajesUseCase",
    "SubirAdjuntoUseCase",
    "ListarAdjuntosUseCase",
    "EliminarAdjuntoUseCase",
    # Notificaciones (10)
    "CrearNotificacionUseCase",
    "ObtenerNotificacionUseCase",
    "ListarNotificacionesUseCase",
    "MarcarNotificacionLeidaUseCase",
    "MarcarTodasLeidasUseCase",
    "ContarNoLeidasUseCase",
    "CrearNotificacionProgramadaUseCase",
    "CancelarNotificacionProgramadaUseCase",
    "ProcesarNotificacionesProgramadasUseCase",
    "ListarTiposNotificacionesUseCase",
    "AgruparNotificacionesPorTipoUseCase",
    "EnviarNotificacionMasivaUseCase",
    # Estadísticas (2)
    "ObtenerEstadisticasUsuarioUseCase",
    "ObtenerEstadisticasSedeUseCase",
]
