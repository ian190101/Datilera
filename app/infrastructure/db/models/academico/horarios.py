from sqlalchemy import Column, DateTime, Integer, String, Time, func

from app.infrastructure.db.base import Base


class Horario(Base):
    """Franja horaria reutilizable por los módulos académicos."""

    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True, index=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
