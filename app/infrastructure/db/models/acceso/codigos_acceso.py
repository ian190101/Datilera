# app/infrastructure/db/models/acceso/codigos_acceso.py
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey,
    UniqueConstraint, Enum as SQLEnum, func
)
from app.infrastructure.db.base import Base
import enum

class EstadoCodigo(enum.Enum):
    pendiente = "pendiente"
    enviado = "enviado"
    consumido = "consumido"
    expirado = "expirado"
    revocado = "revocado"

class CodigoAcceso(Base):
    __tablename__ = "codigos_acceso"
    __table_args__ = (UniqueConstraint("codigo", name="uq_codigo_acceso"),)

    id = Column(Integer, primary_key=True, autoincrement=True)

    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    gestion = Column(Integer, nullable=False, index=True)

    # A qué rol habilita el código
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Para profesoras/otros puede apuntar a una persona concreta ya registrada (usuario destino)
    usuario_destino_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=True, index=True)

    # Caso tutores: código por estudiante, permite múltiples cuentas
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="RESTRICT"), nullable=True, index=True)
    max_cuentas = Column(Integer, nullable=False, default=1)
    cuentas_creadas = Column(Integer, nullable=False, default=0)

    # Token y vigencia
    codigo = Column(String(8), nullable=False, unique=True, index=True)
    expira_en = Column(Date, nullable=True, index=True)
    estado = Column(SQLEnum(EstadoCodigo), nullable=False, default=EstadoCodigo.pendiente, server_default="pendiente", index=True)

    # WhatsApp obligatorio
    whatsapp_numero = Column(String(20), nullable=False, index=True)      # 5917XXXXXXX
    whatsapp_message_id = Column(String(100), nullable=True, index=True)
    enviado = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    enviado_en = Column(DateTime, nullable=True, index=True)

    entregado_a = Column(String(140), nullable=True)
    observaciones = Column(Text, nullable=True)
    creado_por = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class CodigoAccesoUso(Base):
    __tablename__ = "codigos_acceso_usos"
    __table_args__ = (UniqueConstraint("codigo_id", "usuario_id", name="uq_codigo_usuario"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_id = Column(Integer, ForeignKey("codigos_acceso.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True)
    consumido_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)
