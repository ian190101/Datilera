from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func
from app.infrastructure.db.base import Base

class Consentimiento(Base):
    __tablename__ = "consentimientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False, index=True)
    tutor_id = Column(Integer, ForeignKey("tutores.id", ondelete="RESTRICT"), nullable=False, index=True)

    tipo = Column(String(80), nullable=False, index=True)  # p.ej. "salidas", "uso_imagen", "medicacion"
    descripcion = Column(Text, nullable=True)
    firmado = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    firma_url = Column(String(255), nullable=True)

    firmado_en = Column(DateTime, nullable=True, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
