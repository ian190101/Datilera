# app/kernel/domain/seguridad/user_entidad.py
from __future__ import annotations

from datetime import UTC, datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from .preferencias_usuario_entidad import PreferenciasUsuario
from .rol_entidad import Accion, Rol


class Usuario(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    nombre_usuario: str
    nombres: str
    apellidos: str
    email: str | None = None
    telefono: str | None = None
    contrasena: str
    roles: list[Rol] = Field(default_factory=list)
    sede_id: int
    sede_nombre: str = "Principal"
    activo: bool = True
    debe_cambiar_password: bool = False
    foto_perfil: str | None = None

    fecha_creacion: AwareDatetime = Field(default_factory=lambda: datetime.now(UTC))
    ultimo_login: AwareDatetime | None = None

    preferencias: PreferenciasUsuario = Field(default_factory=PreferenciasUsuario)

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"

    @property
    def lista_permisos(self) -> list[str]:
        """Devuelve una lista plana de permisos ej: ['Inscripcion:Ver']"""
        permisos_set = set()
        for rol in self.roles:
            for permiso in rol.permisos:
                # Usa el nombre_completo que arreglamos en permiso_entidad
                permisos_set.add(permiso.nombre_completo)
        return list(permisos_set)

    @field_validator("foto_perfil")
    @classmethod
    def _ext_imagen(cls, v: str | None) -> str | None:
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
