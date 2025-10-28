from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint, Boolean, func
from app.infrastructure.db.base import Base

class AlumnoParalelo(Base):
    __tablename__ = "alumnos_paralelos"
    __table_args__ = (
        UniqueConstraint("alumno_id", "paralelo_id", "gestion", name="uq_alumno_paralelo_gestion"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False, index=True)
    paralelo_id = Column(Integer, ForeignKey("paralelos.id", ondelete="RESTRICT"), nullable=False, index=True)
    gestion = Column(Integer, nullable=False, index=True)

    fecha_ingreso = Column(Date, nullable=True, index=True)
    fecha_salida = Column(Date, nullable=True, index=True)
    actual = Column(Boolean, nullable=False, default=True, server_default="1", index=True)

    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
