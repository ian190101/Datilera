# app/kernel/domain/seguridad/user_entidad.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, field_validator

from .rol_entidad import Rol, Accion
from .preferencias_usuario_entidad import PreferenciasUsuario


class Usuario(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    nombre_usuario: str
    nombres: str 
    apellidos: str
    email: Optional[str] = None
    contrasena: str
    roles: List[Rol] = []
    sede_id: int
    sede_nombre: str = "Principal"
    activo: bool = True
    foto_perfil: Optional[str] = None

    fecha_creacion: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ultimo_login: Optional[AwareDatetime] = None

    preferencias: PreferenciasUsuario = Field(default_factory=PreferenciasUsuario)

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def lista_permisos(self) -> List[str]:
        """Devuelve una lista plana de permisos ej: ['Inscripcion:Ver']"""
        permisos_set = set()
        for rol in self.roles:
            for permiso in rol.permisos:
                # Usa el nombre_completo que arreglamos en permiso_entidad
                permisos_set.add(permiso.nombre_completo)
        return list(permisos_set)

    @field_validator("foto_perfil")
    @classmethod
    def _ext_imagen(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.lower().endswith((".jpg", ".jpeg", ".png")):
            raise ValueError("Formato de imagen no válido")
        return v

    def cambiar_contrasena(self, nueva_contrasena: str) -> None:
        self.contrasena = nueva_contrasena

    def desactivar(self) -> None:
        self.activo = False

    def activar(self) -> None:
        self.activo = True

    def cambiar_foto(self, nueva_foto: str) -> None:
        self.foto_perfil = nueva_foto  # validador asegura extensión válida

    def tiene_permiso(self, recurso: str, accion: Accion) -> bool:
        # Nota: Aquí 'recurso' es el argumento que pasas, comparamos con 'vista' del permiso
        # Buscamos si alguno de los roles tiene ese permiso específico
        for rol in self.roles:
            for p in rol.permisos:
                if p.vista == recurso and p.accion == accion:
                    return True
        return False