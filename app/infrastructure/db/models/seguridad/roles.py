from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class Rol(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    codigos_acceso = relationship(
    "CodigoAcceso",
    back_populates="rol",
    lazy="select",
    )
    usos_codigos_acceso = relationship(
        "CodigoAccesoUso",
        back_populates="rol",
        lazy="select",
    )

    # 1. Directa
    usuarios = relationship(
        "Usuario",
        secondary="usuarios_roles",
        back_populates="roles",
        lazy="select",
        viewonly=True
    )

    # 2. Intermedia (Nueva)
    usuarios_asociados = relationship(
        "UsuarioRol",
        back_populates="rol",
        cascade="all, delete-orphan",
        lazy="noload"
    )
    # 1. Relación Directa (La que usas en el código: rol.permisos)
    permisos = relationship(
        "Permiso",
        secondary="roles_permisos", # <--- Asegúrate que este sea el nombre de la tabla
        back_populates="roles",     # <--- Apunta a "roles" en la clase Permiso
        lazy="noload",
        viewonly=True               # <--- IMPORTANTE para evitar conflictos de escritura
    )

    # 2. Relación Intermedia (La técnica: rol.permisos_asociados)
    permisos_asociados = relationship(
        "RolPermiso",
        back_populates="rol",
        cascade="all, delete-orphan",
        lazy="noload"
    )