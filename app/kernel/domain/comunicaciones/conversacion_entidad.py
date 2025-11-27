# app/kernel/domain/comunicaciones/conversacion_entidad.py

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EstadoConversacion(str, Enum):
    """Estados válidos para una conversación."""
    ABIERTA = "abierta"
    CERRADA = "cerrada"


class TipoConversacion(str, Enum):
    """Tipos de conversación."""
    DIRECTO = "directo"  # 1 a 1
    GRUPO = "grupo"  # Múltiples participantes
    SISTEMA = "sistema"  # Mensajes automáticos


class Participante(BaseModel):
    """VO para participantes de una conversación."""
    usuario_id: int
    rol: str  # 'profesora', 'tutor', 'directora'
    sede_id: Optional[int] = None
    
    model_config = ConfigDict(frozen=True)

    def puede_enviar(self) -> bool:
        """Determina si el participante puede enviar mensajes."""
        return True  # Reglas avanzadas se orquestan en servicios


class Conversacion(BaseModel):
    """Entidad **Conversación**.

    Historias:
    - **US-COM-001** Crear conversación (asunto obligatorio, ≥2 participantes, estado `abierta`, por sede).
    - **US-COM-006** Cerrar conversación (bloquea interacción).
    - **US-COM-007** Listado/orden por `ultima_actividad_en`.
    - Chat profesora–tutor con intervención de la directora cuando corresponda.
    """

    id: int
    sede_id: int
    asunto: str
    participantes: List[Participante]
    tipo: TipoConversacion = TipoConversacion.DIRECTO
    estado: EstadoConversacion = EstadoConversacion.ABIERTA
    creado_por_id: int
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)
    ultima_actividad_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )

    @field_validator("asunto")
    @classmethod
    def _asunto_valido(cls, v: str) -> str:
        """Valida asunto obligatorio (US-COM-001)."""
        asunto_limpio = (v or "").strip()
        if not asunto_limpio:
            raise ValueError("El asunto no puede estar vacío (US-COM-001).")
        if len(asunto_limpio) > 120:
            raise ValueError("El asunto no puede superar 120 caracteres (US-COM-001).")
        return asunto_limpio

    @field_validator("participantes")
    @classmethod
    def _min_participantes(cls, v: List[Participante]) -> List[Participante]:
        """Valida mínimo 2 participantes (US-COM-001)."""
        if not v or len(v) < 2:
            raise ValueError(
                "Una conversación requiere al menos 2 participantes (US-COM-001)."
            )
        return v

    # --- Reglas/acceso ---
    def es_participante(self, usuario_id: int) -> bool:
        """Verifica si un usuario es participante."""
        return any(p.usuario_id == usuario_id for p in self.participantes)

    def esta_cerrada(self) -> bool:
        """Verifica si la conversación está cerrada."""
        return self.estado == EstadoConversacion.CERRADA

    # --- Comportamiento ---
    def agregar_participante(self, nuevo: Participante) -> None:
        """Agrega un participante si no existe."""
        if any(p.usuario_id == nuevo.usuario_id for p in self.participantes):
            return
        self.participantes.append(nuevo)
        self.touch()

    def remover_participante(self, usuario_id: int) -> None:
        """Remueve un participante."""
        self.participantes = [p for p in self.participantes if p.usuario_id != usuario_id]
        self.touch()

    def cerrar(self, usuario_id: int) -> None:
        """Cierra la conversación (US-COM-006)."""
        if not self.es_participante(usuario_id):
            raise ValueError(
                "Solo un participante puede cerrar la conversación (US-COM-006)."
            )
        if self.estado == EstadoConversacion.CERRADA:
            return
        self.estado = EstadoConversacion.CERRADA
        self.actualizado_en = datetime.utcnow()

    def reabrir(self, usuario_id: int) -> None:
        """Reabre la conversación."""
        if not self.es_participante(usuario_id):
            raise ValueError("Solo un participante puede reabrir la conversación.")
        if self.estado == EstadoConversacion.ABIERTA:
            return
        self.estado = EstadoConversacion.ABIERTA
        self.actualizado_en = datetime.utcnow()

    def touch(self) -> None:
        """Actualiza `ultima_actividad_en` (US-COM-007)."""
        ahora = datetime.utcnow()
        self.ultima_actividad_en = ahora
        self.actualizado_en = ahora
