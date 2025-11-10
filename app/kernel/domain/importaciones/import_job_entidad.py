# app/kernel/domain/importaciones/import_job_entidad.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Iterable


class EstadoImportacion(str, Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"


class TransicionInvalidaError(Exception):
    """Se intentó una transición inválida de estado del import job."""


@dataclass
class ImportJob:
    """
    Entidad **ImportJob**.

    Invariantes y reglas:
    - Ciclo de vida: PENDIENTE -> PROCESANDO -> (COMPLETADO | ERROR)
    - `nombre_archivo`, `tipo_importacion`, `archivo_url` obligatorios.
    - Conteos no negativos (acumulativos).
    - El `log_errores` se acumula con marcas de tiempo (texto plano).
    """
    id: int
    usuario_id: int
    nombre_archivo: str
    tipo_importacion: str
    archivo_url: str
    estado: EstadoImportacion = EstadoImportacion.PENDIENTE
    registros_procesados: int = 0
    registros_fallidos: int = 0
    log_errores: Optional[str] = None
    creado_en: datetime = None
    completado_en: Optional[datetime] = None

    # --- Inicialización / validación básica ---
    def __post_init__(self):
        if not (self.nombre_archivo or "").strip():
            raise ValueError("El nombre del archivo es obligatorio.")
        if not (self.tipo_importacion or "").strip():
            raise ValueError("El tipo de importación es obligatorio.")
        if not (self.archivo_url or "").strip():
            raise ValueError("La URL del archivo es obligatoria.")
        if self.registros_procesados < 0 or self.registros_fallidos < 0:
            raise ValueError("Los conteos no pueden ser negativos.")
        self.creado_en = self.creado_en or datetime.utcnow()

    # --- Transiciones de estado ---
    def iniciar_proceso(self) -> None:
        if self.estado != EstadoImportacion.PENDIENTE:
            raise TransicionInvalidaError("Solo se puede iniciar desde PENDIENTE.")
        self.estado = EstadoImportacion.PROCESANDO

    def marcar_completado(self) -> None:
        if self.estado != EstadoImportacion.PROCESANDO:
            raise TransicionInvalidaError("Solo se puede completar desde PROCESANDO.")
        self.estado = EstadoImportacion.COMPLETADO
        self.completado_en = datetime.utcnow()

    def marcar_error(self, mensaje: Optional[str] = None) -> None:
        if self.estado not in (EstadoImportacion.PENDIENTE, EstadoImportacion.PROCESANDO):
            raise TransicionInvalidaError("Solo se puede marcar ERROR desde PENDIENTE o PROCESANDO.")
        self.estado = EstadoImportacion.ERROR
        if mensaje:
            self._append_error(mensaje)
        self.completado_en = datetime.utcnow()

    # --- Progreso y errores ---
    def registrar_progreso(
        self,
        procesados_delta: int = 0,
        fallidos_delta: int = 0,
        errores: Optional[Iterable[str]] = None,
    ) -> None:
        if self.estado != EstadoImportacion.PROCESANDO:
            raise TransicionInvalidaError("El progreso solo se registra en PROCESANDO.")
        if procesados_delta < 0 or fallidos_delta < 0:
            raise ValueError("Los incrementos deben ser no negativos.")
        self.registros_procesados += procesados_delta
        self.registros_fallidos += fallidos_delta
        if errores:
            for e in errores:
                if e and e.strip():
                    self._append_error(e)

    # --- Utilidades internas ---
    def _append_error(self, mensaje: str) -> None:
        stamp = datetime.utcnow().isoformat(timespec="seconds")
        line = f"[{stamp}] {mensaje.strip()}"
        if self.log_errores and self.log_errores.strip():
            self.log_errores += "\n" + line
        else:
            self.log_errores = line