# app/kernel/domain/inscripcion/formulario_inscripcion_entidad.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
class EstadoFormulario(str, Enum):
    BORRADOR = "borrador"
    ENVIADO = "enviado"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


class TransicionInvalidaError(Exception):
    """Se intentó una transición de estado inválida."""


class FormularioInscripcion:
    """
    Entidad **FormularioInscripcion**.

    Flujo (según requerimientos):
    - Estados: BORRADOR -> ENVIADO -> (APROBADO | RECHAZADO)
    - La directora puede **agregar observaciones**.
    - Aprobación permite posterior **emisión de contrato** (otra entidad).
    """

    def __init__(
        self,
        id: int,
        alumno_id: int,
        sede_id: int,
        gestion: int,
        estado: EstadoFormulario = EstadoFormulario.BORRADOR,
        observaciones: Optional[str] = None,
        creado_en: Optional[datetime] = None,
        actualizado_en: Optional[datetime] = None,
    ):
        if gestion <= 0:
            raise ValueError("La gestión debe ser un entero positivo.")
        self.id = id
        self.alumno_id = alumno_id
        self.sede_id = sede_id
        self.gestion = gestion
        self.estado = estado
        self.observaciones = (observaciones or "").strip() or None
        self.creado_en = creado_en or datetime.utcnow()
        self.actualizado_en = actualizado_en or self.creado_en

    # --- Comportamiento de dominio ---
    def enviar(self) -> None:
        if self.estado != EstadoFormulario.BORRADOR:
            raise TransicionInvalidaError("Solo se puede ENVIAR desde BORRADOR.")
        self.estado = EstadoFormulario.ENVIADO
        self.actualizado_en = datetime.utcnow()

    def aprobar(self) -> None:
        if self.estado != EstadoFormulario.ENVIADO:
            raise TransicionInvalidaError("Solo se puede APROBAR desde ENVIADO.")
        self.estado = EstadoFormulario.APROBADO
        self.actualizado_en = datetime.utcnow()

    def rechazar(self, motivo: Optional[str] = None) -> None:
        if self.estado != EstadoFormulario.ENVIADO:
            raise TransicionInvalidaError("Solo se puede RECHAZAR desde ENVIADO.")
        self.estado = EstadoFormulario.RECHAZADO
        if motivo:
            self.agregar_observacion(f"[RECHAZADO] {motivo}")
        self.actualizado_en = datetime.utcnow()

    def agregar_observacion(self, texto: str) -> None:
        texto = (texto or "").strip()
        if not texto:
            return
        if self.observaciones:
            self.observaciones += f"\n{'text'}"
        else:
            self.observaciones = texto
        self.actualizado_en = datetime.utcnow()