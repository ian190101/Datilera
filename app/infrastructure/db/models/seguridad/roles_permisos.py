from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, UniqueConstraint
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class RolPermiso(Base):
    __tablename__ = "roles_permisos"
    __table_args__ = (
        UniqueConstraint("rol_id", "permiso_id", name="uq_rol_permiso"),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permiso_id = Column(Integer, ForeignKey("permisos.id", ondelete="CASCADE"), nullable=False, index=True)
    asignado_en = Column(DateTime, nullable=False, server_default=func.now())

    # Conecta con permisos_asociados en Rol
    rol = relationship("Rol", back_populates="permisos_asociados") 
    
    # Conecta con roles_asociados en Permiso (ver paso 3)
    permiso = relationship("Permiso", back_populates="roles_asociados")
