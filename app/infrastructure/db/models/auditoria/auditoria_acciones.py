# app/infrastructure/db/models/auditoria/auditoria_acciones.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, func, Index
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship


class AuditoriaAccion(Base):
    """
    Modelo de auditoría completo para trazabilidad end-to-end.
    
    Según HU:
    - Se necesitan auditar TODAS las acciones
    - Ver quién hace qué, cuándo y desde dónde
    - Logs para servicio técnico
    - Inmutabilidad de registros
    """
    __tablename__ = "auditoria_acciones"

    # ===== EXISTENTES =====
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    entidad = Column(String(120), nullable=False, index=True)  # "pagos", "alumnos", "items"
    entidad_id = Column(String(64), nullable=True, index=True)
    accion = Column(String(30), nullable=False, index=True)  # "create", "update", "delete", "login"
    datos_antes = Column(JSON, nullable=True)
    datos_despues = Column(JSON, nullable=True)
    ip = Column(String(50), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    sesion_id = Column(Integer, ForeignKey("sesiones.id", ondelete="SET NULL"), nullable=True, index=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    # ===== NUEVAS COLUMNAS (según HU) =====
    
    # Nivel de severidad (para filtrar logs críticos)
    nivel = Column(String(20), nullable=False, default="info", index=True)
    # Valores: "debug", "info", "warning", "error", "critical"
    
    # Método HTTP (para auditoría de API)
    metodo_http = Column(String(10), nullable=True, index=True)
    # Valores: "GET", "POST", "PUT", "DELETE", "PATCH"
    
    # Endpoint llamado (ruta completa)
    endpoint = Column(String(255), nullable=True, index=True)
    # Ejemplo: "/api/v1/pagos/123"
    
    # Código de respuesta HTTP
    codigo_respuesta = Column(Integer, nullable=True, index=True)
    # Ejemplo: 200, 201, 400, 401, 500
    
    # Duración de la operación (milisegundos)
    duracion_ms = Column(Integer, nullable=True)
    
    # Descripción legible del evento
    descripcion = Column(Text, nullable=True)
    # Ejemplo: "Usuario Juan Pérez actualizó pago #123"
    
    # Tags para categorización flexible
    tags = Column(JSON, nullable=True)
    # Ejemplo: ["pago", "mora", "recordatorio"]
    
    # Contexto adicional (metadata flexible)
    contexto = Column(JSON, nullable=True)
    # Ejemplo: {"modulo": "pagos", "tipo_pago": "mensualidad"}
    
    # Éxito de la operación
    exitoso = Column(Boolean, nullable=False, default=True, index=True)
    
    # Mensaje de error (si aplica)
    mensaje_error = Column(Text, nullable=True)
    
    # Stack trace completo (solo para errores)
    stack_trace = Column(Text, nullable=True)
    
    # Datos del dispositivo (para app móvil)
    dispositivo_info = Column(JSON, nullable=True)
    # Ejemplo: {"tipo": "mobile", "modelo": "iPhone 13", "os": "iOS 15.2"}
    
    # Geolocalización aproximada (ciudad/país)
    geolocalizacion = Column(JSON, nullable=True)
    # Ejemplo: {"ciudad": "Cochabamba", "pais": "Bolivia"}

    # ===== ÍNDICES COMPUESTOS (para consultas eficientes) =====
    __table_args__ = (
        # Búsqueda por usuario + fecha
        Index('idx_auditoria_usuario_fecha', 'usuario_id', 'creado_en'),
        
        # Búsqueda por sede + entidad + fecha
        Index('idx_auditoria_sede_entidad_fecha', 'sede_id', 'entidad', 'creado_en'),
        
        # Búsqueda por nivel + fecha (para logs críticos)
        Index('idx_auditoria_nivel_fecha', 'nivel', 'creado_en'),
        
        # Búsqueda por éxito + fecha (para errores)
        Index('idx_auditoria_exitoso_fecha', 'exitoso', 'creado_en'),
        
        # Búsqueda por acción + entidad
        Index('idx_auditoria_accion_entidad', 'accion', 'entidad'),
    )

    usuario = relationship("Usuario", back_populates="auditoria_acciones")
    #sede = relationship("Sede", back_populates="logs_auditoria_acciones")
    #sesion = relationship("AuditoriaSesion", back_populates="acciones", foreign_keys="[AuditoriaAccion.sesion_id]")
    cambios = relationship("AuditoriaCambio", back_populates="accion", cascade="all, delete-orphan", lazy="select")


