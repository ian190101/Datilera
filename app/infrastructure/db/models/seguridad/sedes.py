from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.infrastructure.db.base import Base
from sqlalchemy.orm import relationship

class Sede(Base):
    __tablename__ = "sedes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    nombre = Column(String(120), nullable=False)
    direccion = Column(String(250), nullable=True)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    config_alerta_vencimiento_dias = Column(String(15), nullable=True, server_default="5,3,1")
    # =========================================================================
    # RELACIONES
    # =========================================================================
    
    # ---------------------------------------------------------------------------
    # MÓDULO: FINANZAS
    # ---------------------------------------------------------------------------
    descuentos = relationship(
        "Descuento",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Descuentos aplicados en esta sede"
    )
    
    planes_pago = relationship(
        "PlanPagoPersonalizado",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Planes de pago personalizados de la sede"
    )
    
    prorrateos = relationship(
        "Prorrateo",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Cálculos de prorrateo de la sede"
    )
    
    '''''
    pagos = relationship(
    "Pago",
    primaryjoin="Sede.id == Pago.sede_id",
    foreign_keys="Pago.sede_id",
    lazy="noload",
    viewonly=True,
    doc="Pagos realizados en la sede"
    )
    

    conceptos_pago = relationship(
        "ConceptoPago",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Conceptos de pago configurados en la sede"
    )
    '''''

    categorias_pago = relationship("CategoriaPago", back_populates="sede", lazy="select")
    #categorías_egreso = relationship("CategoríaEgreso", back_populates="sede", lazy="select")
    movimientos_caja = relationship("LibroCaja", back_populates="sede", lazy="select")
    planes_pago_personalizados = relationship("PlanPagoPersonalizado", back_populates="sede", lazy="select") 
    # ---------------------------------------------------------------------------
    # MÓDULO: ALUMNOS
    # ---------------------------------------------------------------------------
    alumnos = relationship(
        "Alumno",
        back_populates="sede",
        lazy="select",
        doc="Alumnos inscritos en la sede"
    )
    
    asistencias_alumnos = relationship(
        "AsistenciaAlumno",
        back_populates="sede",
        lazy="select",
        doc="Registros de asistencia de alumnos"
    )
    
    # ---------------------------------------------------------------------------
    # MÓDULO: CALENDARIO Y PLANIFICACIÓN
    # ---------------------------------------------------------------------------
    tipos_eventos = relationship(
        "TipoEvento",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Tipos de eventos configurados en la sede"
    )
    
    eventos_calendario = relationship(
        "EventoCalendario",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Eventos del calendario de la sede"
    )
    
    planificaciones_actividades = relationship(
        "PlanificacionActividad",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Planificaciones de actividades de la sede"
    )
    
    # ---------------------------------------------------------------------------
    # MÓDULO: ACADÉMICO
    # ---------------------------------------------------------------------------
    '''''
    cursos = relationship(
        "Curso",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Cursos/Niveles de la sede"
    )
    '''''

    paralelos = relationship(
        "Paralelo",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Paralelos/Secciones de la sede"
    )
    
    
    turnos = relationship(
        "Turno",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Turnos de la sede (mañana/tarde)"
    )
    grupos = relationship("Grupo", back_populates="sede", lazy="select")
    
    # ---------------------------------------------------------------------------
    # MÓDULO: USUARIOS Y PERSONAL
    # ---------------------------------------------------------------------------
    usuarios = relationship(
        "Usuario",
        back_populates="sede",
        lazy="select",
        doc="Usuarios asignados a la sede"
    )
    
    asistencias_personal = relationship(
        "AsistenciaPersonal",
        back_populates="sede",
        lazy="select",
        doc="Registros de asistencia del personal"
    )
    
    permisos_personal = relationship(
        "PermisoPersonal",
        back_populates="sede",
        lazy="select",
        doc="Permisos solicitados por el personal"
    )
    conversaciones = relationship("Conversacion", back_populates="sede", lazy="select")


    # ---------------------------------------------------------------------------
    # MÓDULO: NOTIFICACIONES
    # ---------------------------------------------------------------------------
    '''''
    notificaciones = relationship(
        "Notificacion",
        back_populates="sede",
        lazy="select",
        doc="Notificaciones de la sede"
    )
    

    tipos_notificaciones = relationship(
        "TipoNotificacion",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Tipos de notificaciones configurados"
    )
    '''''
    # ---------------------------------------------------------------------------
    # MÓDULO: INVENTARIOS
    # ---------------------------------------------------------------------------
    '''''
    productos = relationship(
        "Producto",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Productos del inventario de la sede"
    )
    
    
    categorias_producto = relationship(
        "CategoriaProducto",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Categorías de productos de la sede"
    )
    
    movimientos_inventario = relationship(
        "MovimientoInventario",
        back_populates="sede",
        lazy="select",
        doc="Movimientos de inventario de la sede"
    )
'''''

    stock_items = relationship("StockSede", back_populates="sede", lazy="select")
    movimientos_stock = relationship("MovimientoStock", back_populates="sede", lazy="select")
    alertas_stock = relationship("AlertaStock", back_populates="sede", lazy="select")
    alertas_vencimiento = relationship("AlertaVencimiento", back_populates="sede", lazy="select")
        
    '''''
    proveedores = relationship(
        "Proveedor",
        back_populates="sede",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Proveedores de la sede"
    )
    '''''
    
    # ---------------------------------------------------------------------------
    # MÓDULO: COMUNICACIONES
    # ---------------------------------------------------------------------------
    '''''
    mensajes_enviados = relationship(
        "MensajeMasivo",
        back_populates="sede",
        lazy="select",
        doc="Mensajes masivos enviados desde la sede"
    )
    '''''

    # ---------------------------------------------------------------------------
    # MÓDULO: REPORTES Y AUDITORÍA
    # ---------------------------------------------------------------------------
    ''' logs_auditoria = relationship(
        "LogAuditoria",
        back_populates="sede",
        lazy="select",
        doc="Logs de auditoría de la sede"
    )
    '''

    auditoria_sesiones = relationship("AuditoriaSesion", back_populates="sede", lazy="select")
    auditoria_exportaciones = relationship("AuditoriaExportacion", back_populates="sede", lazy="select")
    auditoria_prompts_ia = relationship("AuditoriaPromptIA", back_populates="sede", lazy="select")

    codigos_acceso = relationship(
    "CodigoAcceso",
    back_populates="sede",
    lazy="select",
)
    cursos_extra = relationship("CursoExtra", back_populates="sede", lazy="select")
    alumnos_externos = relationship("AlumnoExterno", back_populates="sede", lazy="select")
    ia_consultas = relationship("IAConsulta", back_populates="sede", lazy="select")
    formularios_inscripcion = relationship("FormularioInscripcion", back_populates="sede", lazy="select")
    contratos_inscripcion = relationship("Contrato", back_populates="sede", lazy="select")
    egresos = relationship("Egreso", back_populates="sede", cascade="all, delete-orphan")
    paralelos = relationship("Paralelo", back_populates="sede", lazy="noload")
    #arqueos = relationship("Arqueos", back_populates="arqueos", cascade="all, delete-orphan")

