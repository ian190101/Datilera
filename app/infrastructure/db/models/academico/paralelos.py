from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class Paralelo(Base):
    __tablename__ = "paralelos"
    __table_args__ = (
        UniqueConstraint("grupo_id", "letra", name="uq_grupo_letra"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="RESTRICT"), nullable=False, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False, index=True)
    letra = Column(String(5), nullable=False, index=True)  # p.ej. "A", "B"
    capacidad = Column(Integer, nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1", index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones CORRECTAS
    sede = relationship("Sede", back_populates="paralelos")  # ← apunta a la relación en Sede
    grupo = relationship("Grupo", back_populates="paralelos")  # ← apunta a Grupo

    # Relaciones hijas (correctas)
    alumnos_paralelos = relationship("AlumnoParalelo", back_populates="paralelo", cascade="all, delete-orphan")
    #paralelos_profesoras = relationship("Paralelos_Profesoras", back_populates="paralelo", cascade="all, delete-orphan")
    planificaciones = relationship("PlanificacionActividad", back_populates="paralelo", lazy="noload")
