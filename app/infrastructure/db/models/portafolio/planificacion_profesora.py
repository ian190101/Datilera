from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum as SQLEnum
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship
import enum

class DuracionPlanificacion(str, enum.Enum):
    MES_1 = "1 Mes"
    MES_3 = "3 Meses"
    MES_6 = "6 Meses"
    GESTION = "Gestión Completa"

class PlanificacionProfesora(Base):
    __tablename__ = "planificaciones_profesoras"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profesora_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True)
    duracion = Column(SQLEnum(DuracionPlanificacion), nullable=False)
    archivo_url = Column(String(255), nullable=False)
    titulo = Column(String(150), nullable=True) # Opcional, por si quieren ponerle nombre
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    profesora = relationship("Usuario")