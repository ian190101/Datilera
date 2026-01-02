# app/kernel/domain/comunicaciones/ports.py

"""
Puertos (interfaces) para el módulo de Comunicaciones.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any

from .conversacion_entidad import Conversacion, Participante, EstadoConversacion
from .mensaje_entidad import Mensaje, TipoMensaje
from .mensaje_adjunto_entidad import MensajeAdjunto, TipoAdjunto
from .notificacion_entidad import Notificacion, CanalNotificacion, EstadoNotificacion


# ==========================
# Repositorio: Conversaciones
# ==========================

class ConversacionRepositoryPort(ABC):
    """Puerto para repositorio de conversaciones."""

    @abstractmethod
    async def crear(
        self,
        sede_id: int,
        asunto: str,
        creado_por_id: int,
        participantes: List[Participante],
        titulo: Optional[str] = None,
        descripcion: Optional[str] = None,
    ) -> Conversacion:
        """Crea una conversación en estado ABIERTA (US-COM-001)."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_id(self, conversacion_id: int) -> Optional[Conversacion]:
        """Obtiene conversación por ID."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_usuario(
        self,
        usuario_id: int,
        sede_id: Optional[int] = None,
        cerradas: Optional[bool] = None,
        limite: int = 20,
        offset: int = 0,
    ) -> List[Conversacion]:
        """Lista conversaciones donde el usuario es participante (US-COM-007)."""
        raise NotImplementedError

    @abstractmethod
    async def guardar(self, conversacion: Conversacion) -> Conversacion:
        """Persiste cambios de la conversación."""
        raise NotImplementedError

    @abstractmethod
    async def cerrar(self, conversacion_id: int, usuario_id: int) -> None:
        """Cierra la conversación (US-COM-006)."""
        raise NotImplementedError

    @abstractmethod
    async def reabrir(self, conversacion_id: int, usuario_id: int) -> None:
        """Reabre una conversación cerrada."""
        raise NotImplementedError

    @abstractmethod
    async def touch(self, conversacion_id: int) -> None:
        """Actualiza ultima_actividad_en (US-COM-007)."""
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_asunto(
        self, usuario_id: int, termino: str, limite: int = 20
    ) -> List[Conversacion]:
        """Busca conversaciones por asunto."""
        raise NotImplementedError

    @abstractmethod
    async def contar_por_usuario(
        self, usuario_id: int, cerradas: Optional[bool] = None
    ) -> int:
        """Cuenta conversaciones del usuario."""
        raise NotImplementedError


# ==========================
# Repositorio: Participantes
# ==========================

class ParticipanteRepositoryPort(ABC):
    """Puerto para repositorio de participantes."""

    @abstractmethod
    async def agregar(
        self, conversacion_id: int, participante: Participante
    ) -> None:
        """Agrega un participante a la conversación."""
        raise NotImplementedError

    @abstractmethod
    async def remover(self, conversacion_id: int, usuario_id: int) -> bool:
        """Remueve un participante de la conversación."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_conversacion(
        self, conversacion_id: int
    ) -> List[Participante]:
        """Lista participantes de una conversación."""
        raise NotImplementedError

    @abstractmethod
    async def es_participante(self, conversacion_id: int, usuario_id: int) -> bool:
        """Verifica si un usuario es participante."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_rol(
        self, conversacion_id: int, usuario_id: int
    ) -> Optional[str]:
        """Obtiene el rol de un participante en la conversación."""
        raise NotImplementedError


# ==========================
# Repositorio: Mensajes
# ==========================

class MensajeRepositoryPort(ABC):
    """Puerto para repositorio de mensajes."""

    @abstractmethod
    async def crear(
        self,
        conversacion_id: int,
        remitente_id: int,
        contenido: str,
        tipo: TipoMensaje = TipoMensaje.TEXTO,
        reply_a_id: Optional[int] = None,
        metadatos: Optional[Dict] = None,
    ) -> Mensaje:
        """Crea un mensaje (US-COM-002)."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_id(self, mensaje_id: int) -> Optional[Mensaje]:
        """Obtiene mensaje por ID."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_conversacion(
        self, conversacion_id: int, limite: int = 50, offset: int = 0
    ) -> List[Mensaje]:
        """Lista mensajes de una conversación."""
        raise NotImplementedError

    @abstractmethod
    async def contar_no_leidos_conversacion(
        self, conversacion_id: int, usuario_id: int
    ) -> int:
        """Cuenta mensajes no leídos en una conversación (US-COM-003)."""
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_contenido(
        self, usuario_id: int, termino: str, limite: int = 20
    ) -> List[Mensaje]:
        """Busca mensajes por contenido."""
        raise NotImplementedError

    @abstractmethod
    async def contar_enviados_recibidos(
        self, usuario_id: int, conversacion_id: Optional[int] = None
    ) -> Dict[str, int]:
        """Cuenta mensajes enviados vs recibidos (estadísticas)."""
        raise NotImplementedError


# ==========================
# Repositorio: Lecturas de Mensajes
# ==========================

class MensajeLecturaRepositoryPort(ABC):
    """Puerto para repositorio de lecturas de mensajes."""

    @abstractmethod
    async def marcar_leido(self, mensaje_id: int, usuario_id: int) -> None:
        """Marca un mensaje como leído (US-COM-003)."""
        raise NotImplementedError

    @abstractmethod
    async def ya_leido(self, mensaje_id: int, usuario_id: int) -> bool:
        """Verifica si un mensaje ya fue leído."""
        raise NotImplementedError

    @abstractmethod
    async def listar_lecturas(self, mensaje_id: int) -> List[Dict[str, any]]:
        """Lista quién leyó el mensaje y cuándo."""
        raise NotImplementedError


# ==========================
# Repositorio: Adjuntos
# ==========================

class MensajeAdjuntoRepositoryPort(ABC):
    """Puerto para repositorio de adjuntos."""

    @abstractmethod
    async def crear(
        self,
        mensaje_id: int,
        tipo: TipoAdjunto,
        url: str,
        nombre_archivo: Optional[str] = None,
        tamano_bytes: Optional[int] = None,
        mime_type: Optional[str] = None,
    ) -> MensajeAdjunto:
        """Crea un adjunto."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_id(self, adjunto_id: int) -> Optional[MensajeAdjunto]:
        """Obtiene adjunto por ID."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_mensaje(self, mensaje_id: int) -> List[MensajeAdjunto]:
        """Lista adjuntos de un mensaje."""
        raise NotImplementedError

    @abstractmethod
    async def eliminar(self, adjunto_id: int) -> bool:
        """Elimina un adjunto."""
        raise NotImplementedError

    @abstractmethod
    async def contar_por_mensaje(self, mensaje_id: int) -> int:
        """Cuenta adjuntos de un mensaje."""
        raise NotImplementedError


# ==========================
# Repositorio: Notificaciones
# ==========================

class NotificacionRepositoryPort(ABC):
    """Puerto para repositorio de notificaciones."""

    @abstractmethod
    async def crear(
        self,
        usuario_id: int,
        titulo: str,
        cuerpo: str,
        tipo: str,
        relacionado_tipo: Optional[str] = None,
        relacionado_id: Optional[int] = None,
        canal: CanalNotificacion = CanalNotificacion.IN_APP,
        prioridad: str = "media",
        programada_para: Optional[datetime] = None,
        metadatos: Optional[Dict] = None,
    ) -> Notificacion:
        """Crea una notificación (US-COM-004)."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_id(self, notificacion_id: int) -> Optional[Notificacion]:
        """Obtiene notificación por ID."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_usuario(
        self,
        usuario_id: int,
        tipo: Optional[str] = None,
        leidas: Optional[bool] = None,
        limite: int = 20,
        offset: int = 0,
    ) -> List[Notificacion]:
        """Lista notificaciones del usuario (US-COM-008)."""
        raise NotImplementedError

    @abstractmethod
    async def guardar(self, notificacion: Notificacion) -> Notificacion:
        """Persiste cambios de la notificación."""
        raise NotImplementedError

    @abstractmethod
    async def marcar_leida(self, notificacion_id: int) -> None:
        """Marca como leída (US-COM-008)."""
        raise NotImplementedError

    @abstractmethod
    async def marcar_todas_leidas(self, usuario_id: int) -> int:
        """Marca todas las notificaciones como leídas."""
        raise NotImplementedError

    @abstractmethod
    async def contar_no_leidas(self, usuario_id: int) -> int:
        """Cuenta notificaciones no leídas."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_programadas_pendientes(
        self, hasta: datetime
    ) -> List[Notificacion]:
        """Obtiene notificaciones programadas pendientes."""
        raise NotImplementedError

    @abstractmethod
    async def contar_por_tipo(self, usuario_id: int) -> Dict[str, int]:
        """Cuenta notificaciones agrupadas por tipo."""
        raise NotImplementedError

    @abstractmethod
    async def listar_tipos_disponibles(self) -> List[str]:
        """Lista tipos de notificaciones disponibles en el sistema."""
        raise NotImplementedError


# ==========================
# Repositorio: Vistas de Notificaciones
# ==========================

class NotificacionVistaRepositoryPort(ABC):
    """Puerto para repositorio de vistas de notificaciones."""

    @abstractmethod
    async def registrar_vista(self, notificacion_id: int, usuario_id: int) -> None:
        """Registra que el usuario vio la notificación."""
        raise NotImplementedError

    @abstractmethod
    async def ya_vista(self, notificacion_id: int, usuario_id: int) -> bool:
        """Verifica si la notificación ya fue vista."""
        raise NotImplementedError

    @abstractmethod
    async def contar_vistas(self, notificacion_id: int) -> int:
        """Cuenta cuántos usuarios vieron la notificación."""
        raise NotImplementedError


# ==========================
# Servicios externos (puertos)
# ==========================

class NotificadorServicePort(ABC):
    """Puerto para servicio de envío de notificaciones."""

    @abstractmethod
    async def enviar_in_app(self, notificacion: Notificacion) -> bool:
        """Envía notificación in-app (campanita)."""
        raise NotImplementedError

    @abstractmethod
    async def enviar_email(
        self, notificacion: Notificacion, destinatario_email: str
    ) -> bool:
        """Envía notificación por email."""
        raise NotImplementedError

    @abstractmethod
    async def enviar_push(
        self, notificacion: Notificacion, dispositivo_token: str
    ) -> bool:
        """Envía notificación push."""
        raise NotImplementedError

    @abstractmethod
    async def enviar_sms(
        self, notificacion: Notificacion, numero_telefono: str
    ) -> bool:
        """Envía notificación por SMS."""
        raise NotImplementedError


class ArchivoStorageServicePort(ABC):
    """Puerto para servicio de almacenamiento de archivos."""

    @abstractmethod
    async def subir_adjunto(
        self,
        archivo_bytes: bytes,
        nombre_archivo: str,
        mime_type: str,
        carpeta: str = "mensajes",
    ) -> str:
        """Sube un archivo adjunto y devuelve la URL."""
        raise NotImplementedError

    @abstractmethod
    async def eliminar_adjunto(self, url: str) -> bool:
        """Elimina un archivo adjunto."""
        raise NotImplementedError

    @abstractmethod
    async def validar_mime_type(self, mime_type: str) -> bool:
        """Valida si el tipo MIME está permitido."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_tamano_maximo(self, tipo_adjunto: TipoAdjunto) -> int:
        """Obtiene el tamaño máximo permitido por tipo."""
        raise NotImplementedError


class WebSocketServicePort(ABC):
    """Puerto para servicio de WebSockets (tiempo real)."""

    @abstractmethod
    async def notificar_nuevo_mensaje(
        self, conversacion_id: int, mensaje: Mensaje
    ) -> None:
        """Notifica a los participantes sobre un nuevo mensaje."""
        raise NotImplementedError

    @abstractmethod
    async def notificar_lectura(
        self, conversacion_id: int, mensaje_id: int, usuario_id: int
    ) -> None:
        """Notifica que un mensaje fue leído."""
        raise NotImplementedError

    @abstractmethod
    async def notificar_escribiendo(
        self, conversacion_id: int, usuario_id: int, escribiendo: bool
    ) -> None:
        """Notifica que un usuario está escribiendo."""
        raise NotImplementedError


class AnalyticsServicePort(ABC):
    """Puerto para servicio de analytics."""

    @abstractmethod
    async def registrar_envio_mensaje(
        self, usuario_id: int, conversacion_id: int, tipo: TipoMensaje
    ) -> None:
        """Registra el envío de un mensaje."""
        raise NotImplementedError

    @abstractmethod
    async def registrar_lectura_mensaje(
        self, usuario_id: int, mensaje_id: int, tiempo_lectura_segundos: int
    ) -> None:
        """Registra la lectura de un mensaje."""
        raise NotImplementedError

    @abstractmethod
    async def registrar_interaccion_notificacion(
        self, usuario_id: int, notificacion_id: int, accion: str
    ) -> None:
        """Registra interacción con notificación (vista, click, dismiss)."""
        raise NotImplementedError

class WebPushServicePort(ABC):
    """Puerto para enviar notificaciones Web Push a navegadores."""

    @abstractmethod
    async def registrar_suscripcion(
        self,
        usuario_id: int,
        sede_id: int,
        endpoint: str,
        claves: Dict[str, Any],
        user_agent: str | None = None,
    ) -> None:
        """Registra o actualiza una suscripción Web Push para un usuario."""

    @abstractmethod
    async def eliminar_suscripcion(self, usuario_id: int, endpoint: str) -> None:
        """Elimina una suscripción específica para un usuario."""

    @abstractmethod
    async def enviar_webpush_a_usuarios(
        self,
        usuario_ids: List[int],
        titulo: str,
        cuerpo: str,
        data: Dict[str, Any] | None = None,
    ) -> int:
        """Envía una notificación Web Push a todas las suscripciones de los usuarios."""