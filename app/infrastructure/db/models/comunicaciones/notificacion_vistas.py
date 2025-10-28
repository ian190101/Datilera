from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from app.infrastructure.db.base import Base

class NotificacionVista(Base):
    __tablename__ = "notificacion_vistas"
    __table_args__ = (
        UniqueConstraint("notificacion_id", "usuario_id", name="uq_notificacion_usuario"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    notificacion_id = Column(Integer, ForeignKey("notificaciones.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    visto_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)
