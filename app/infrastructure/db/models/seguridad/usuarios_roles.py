from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, UniqueConstraint
from app.infrastructure.db.base import Base

class UsuarioRol(Base):
    __tablename__ = "usuarios_roles"
    __table_args__ = (
        UniqueConstraint("usuario_id", "rol_id", name="uq_usuario_rol"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    asignado_en = Column(DateTime, nullable=False, server_default=func.now())
