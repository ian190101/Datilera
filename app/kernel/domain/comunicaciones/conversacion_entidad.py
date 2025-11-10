from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class EstadoConversacion(str, Enum):
    """Estados válidos para una conversación."""
    ABIERTA = "abierta"
    CERRADA = "cerrada"


@dataclass(frozen=True)
class Participante:
    """VO local para participantes de una conversación.

    Mantiene SRP y evita dependencias externas. El rol modela la relación con el hilo
    (p. ej. 'profesora', 'tutor', 'directora').
    """
    usuario_id: int
    rol: str
    sede_id: Optional[int] = None

    def puede_enviar(self) -> bool:
        # Reglas avanzadas se orquestan fuera (servicios/policies).
        return True


class ConversacionCerradaError(Exception):
    """Se intenta operar una conversación cerrada."""


class ParticipanteNoAutorizado(Exception):
    """Un usuario externo intenta operar sobre la conversación."""


class Conversacion:
    """Entidad **Conversación**.

    Historias:
    - **US-COM-001** Crear conversación (asunto obligatorio, ≥2 participantes, estado `abierta`, por sede).
    - **US-COM-006** Cerrar conversación (bloquea interacción).
    - **US-COM-007** Listado/orden por `ultima_actividad_en`.
    - Chat profesora–tutor con intervención de la directora cuando corresponda.
    """

    def __init__(
        self,
        id: int,
        sede_id: int,
        asunto: str,
        participantes: List[Participante],
        estado: EstadoConversacion = EstadoConversacion.ABIERTA,
        creado_en: Optional[datetime] = None,
        actualizado_en: Optional[datetime] = None,
        ultima_actividad_en: Optional[datetime] = None,
    ):
        asunto_limpio = (asunto or "").strip()
        if not asunto_limpio:
            raise ValueError("El asunto no puede estar vacío (US-COM-001).")
        if len(asunto_limpio) > 120:
            raise ValueError("El asunto no puede superar 120 caracteres (US-COM-001).")
        if not participantes or len(participantes) < 2:
            raise ValueError("Una conversación requiere al menos 2 participantes (US-COM-001).")

        self.id = id
        self.sede_id = sede_id
        self.asunto = asunto_limpio
        self.participantes = participantes
        self.estado = estado
        self.creado_en = creado_en or datetime.utcnow()
        self.actualizado_en = actualizado_en or self.creado_en
        self.ultima_actividad_en = ultima_actividad_en or self.creado_en

    # --- Reglas/acceso ---
    def es_participante(self, usuario_id: int) -> bool:
        return any(p.usuario_id == usuario_id for p in self.participantes)

    # --- Comportamiento ---
    def agregar_participante(self, nuevo: Participante) -> None:
        if any(p.usuario_id == nuevo.usuario_id for p in self.participantes):
            return
        self.participantes.append(nuevo)
        self.touch()

    def cerrar(self, usuario_id: int) -> None:
        if not self.es_participante(usuario_id):
            raise ParticipanteNoAutorizado("Solo un participante puede cerrar la conversación (US-COM-006).")
        if self.estado == EstadoConversacion.CERRADA:
            return
        self.estado = EstadoConversacion.CERRADA
        self.actualizado_en = datetime.utcnow()

    def touch(self) -> None:
        """Actualiza `ultima_actividad_en` (US-COM-007)."""
        ahora = datetime.utcnow()
        self.ultima_actividad_en = ahora
        self.actualizado_en = ahora