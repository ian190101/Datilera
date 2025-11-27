# app/kernel/domain/cursosextra/categoria_costo_curso_extra_entidad.py

"""
Entidad de dominio: CategoriaCostoCursoExtra
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class CategoriaCostoCursoExtra(BaseModel):
    """
    Entidad **CategoriaCostoCursoExtra**.
    
    Representa una categoría dinámica de costos/gastos para un curso extra.
    Permite a la directora definir categorías personalizadas por curso
    (ej. Materiales, Instructor, Publicidad, Transporte, etc.).
    
    Reglas:
    - Cada categoría pertenece a un curso específico
    - Los nombres deben ser únicos por curso
    - Se pueden activar/desactivar pero no eliminar si tienen costos asociados
    """
    id: int
    curso_extra_id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
    )
    
    @field_validator("nombre")
    @classmethod
    def _nombre_valido(cls, v: str) -> str:
        """Valida nombre obligatorio."""
        nombre = (v or "").strip()
        if not nombre:
            raise ValueError("El nombre de la categoría es obligatorio.")
        if len(nombre) > 100:
            raise ValueError("El nombre no puede superar 100 caracteres.")
        return nombre
    
    @field_validator("descripcion")
    @classmethod
    def _descripcion_valida(cls, v: Optional[str]) -> Optional[str]:
        """Valida longitud de descripción."""
        if v and len(v) > 500:
            raise ValueError("La descripción no puede superar 500 caracteres.")
        return v
    
    # --- Comportamiento ---
    
    def activar(self) -> None:
        """Activa la categoría."""
        self.activo = True
    
    def desactivar(self) -> None:
        """Desactiva la categoría."""
        self.activo = False
    
    def esta_activa(self) -> bool:
        """Verifica si la categoría está activa."""
        return self.activo
    
    def actualizar_nombre(self, nuevo_nombre: str) -> None:
        """Actualiza el nombre de la categoría."""
        nombre = nuevo_nombre.strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")
        if len(nombre) > 100:
            raise ValueError("El nombre no puede superar 100 caracteres.")
        self.nombre = nombre
