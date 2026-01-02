from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, UniqueConstraint
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class Grupo(Base):
    __tablename__ = "grupos"
    __table_args__ = (
        UniqueConstraint("sede_id", "nombre", "gestion", name="uq_grupo_sede_gestion"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False, index=True)
    nombre = Column(String(80), nullable=False, index=True)   # p.ej. "Inicial-1", "Inicial-2"
    gestion = Column(Integer, nullable=False, index=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    sede = relationship("Sede", back_populates="grupos")  # o "grupos" si prefieres ese nombre en Sede
    paralelos = relationship(
        "Paralelo",
        back_populates="grupo",
        lazy="noload",
        cascade="all, delete-orphan",
    )
    actividades = relationship("Actividad", back_populates="grupo", lazy="select")



    