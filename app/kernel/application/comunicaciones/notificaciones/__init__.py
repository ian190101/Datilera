# app/kernel/application/comunicaciones/notificaciones/__init__.py

from .crear_notificacion import CrearNotificacionUseCase
from .obtener_notificacion import ObtenerNotificacionUseCase
from .listar_notificaciones import ListarNotificacionesUseCase
from .marcar_notificacion_leida import MarcarNotificacionLeidaUseCase
from .marcar_todas_leidas import MarcarTodasLeidasUseCase
from .contar_no_leidas import ContarNoLeidasUseCase
from .crear_notificacion_programada import CrearNotificacionProgramadaUseCase
from .cancelar_notificacion_programada import CancelarNotificacionProgramadaUseCase
from .procesar_notificaciones_programadas import ProcesarNotificacionesProgramadasUseCase
from .listar_tipos_notificaciones import ListarTiposNotificacionesUseCase
from .agrupar_notificaciones_por_tipo import AgruparNotificacionesPorTipoUseCase  # NUEVO
from .enviar_masivo import EnviarNotificacionMasivaUseCase  # NUEVO

__all__ = [
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
    "AgruparNotificacionesPorTipoUseCase",  # NUEVO
    "EnviarNotificacionMasivaUseCase",  # NUEVO
]
