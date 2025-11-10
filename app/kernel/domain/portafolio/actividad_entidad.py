# app/kernel/domain/portafolio/actividad_entidad.py
from __future__ import annotations
from datetime import date, datetime
from typing import Optional


class Actividad:
    """
    Entidad **Actividad** (portafolio).
    - Relacionada a un paralelo y a la profesora que la registra.
    - `titulo` obligatorio (≤150).
    - `fecha_actividad` obligatoria.
    """

    def __init__(
        self,
        id: int,
        paralelo_id: int,
        profesora_id: int,
        titulo: str,
        fecha_actividad: date,
        descripcion: Optional[str] = None,
        creado_en: Optional[datetime] = None,
        actualizado_en: Optional[datetime] = None,
    ):
        t = (titulo or "").strip()
        if not t:
            raise ValueError("El título de la actividad es obligatorio.")
        if len(t) > 150:
            raise ValueError("El título no puede exceder 150 caracteres.")
        self.id = id
        self.paralelo_id = paralelo_id
        self.profesora_id = profesora_id
        self.titulo = t
        self.descripcion = (descripcion or "").strip() or None
        self.fecha_actividad = fecha_actividad
        self.creado_en = creado_en or datetime.utcnow()
        self.actualizado_en = actualizado_en or self.creado_en

    def actualizar_detalle(
        self,
        titulo: Optional[str] = None,
        descripcion: Optional[str] = None,
        fecha_actividad: Optional[date] = None,
    ) -> None:
        if titulo is not None:
            t = (titulo or "").strip()
            if not t:
                raise ValueError("El título no puede quedar vacío.")
            if len(t) > 150:
                raise ValueError("El título no puede exceder 150 caracteres.")
            self.titulo = t
        if descripcion is not None:
            self.descripcion = (descripcion or "").strip() or None
        if fecha_actividad is not None:
            self.fecha_actividad = fecha_actividad
        self.actualizado_en = datetime.utcnow()