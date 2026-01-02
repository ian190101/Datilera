# app/kernel/application/calendario/tipos_eventos/crear_tipo_evento.py

from app.kernel.domain.calendario import (
    TipoEvento,
    TipoEventoRepositoryPort,
    TipoEventoDuplicadoError,
    CalendarioColorInvalidoError,
    CalendarioCampoRequeridoError,
)


class CrearTipoEventoUseCase:
    """Caso de uso: Crear tipo de evento (US-CAL-001).
    
    Reglas:
    - Nombre único por sede
    - Color en formato hexadecimal
    - Solo directora/admin/superadmin pueden crear
    """
    
    def __init__(self, tipo_evento_repo: TipoEventoRepositoryPort):
        self.tipo_evento_repo = tipo_evento_repo
    
    async def ejecutar(
        self,
        nombre: str,
        sede_id: int,
        creado_por: int,
        descripcion: str = None,
        color: str = "#3B82F6",
        icono: str = None,
        requiere_aprobacion: bool = False,
        visible_profesoras: bool = True,
        visible_tutores: bool = True,
    ) -> TipoEvento:
        """Crea un nuevo tipo de evento.
        
        Args:
            nombre: Nombre del tipo de evento
            sede_id: ID de la sede
            creado_por: ID del usuario creador
            descripcion: Descripción (opcional)
            color: Color hexadecimal (default: #3B82F6)
            icono: Nombre del ícono (opcional)
            requiere_aprobacion: Si requiere aprobación de directora
            visible_profesoras: Si es visible para profesoras
            visible_tutores: Si es visible para tutores
            
        Returns:
            TipoEvento creado
            
        Raises:
            CalendarioCampoRequeridoError: Si falta algún campo requerido
            CalendarioColorInvalidoError: Si el color no es válido
            TipoEventoDuplicadoError: Si ya existe un tipo con ese nombre en la sede
        """
        # Validaciones
        if not nombre or not nombre.strip():
            raise CalendarioCampoRequeridoError("nombre")
        
        if not sede_id:
            raise CalendarioCampoRequeridoError("sede_id")
        
        # Validar formato de color
        if color and not self._validar_color_hex(color):
            raise CalendarioColorInvalidoError(color)
        
        # Crear entidad
        tipo = TipoEvento(
            nombre=nombre.strip(),
            descripcion=descripcion,
            color=color,
            icono=icono,
            requiere_aprobacion=requiere_aprobacion,
            visible_profesoras=visible_profesoras,
            visible_tutores=visible_tutores,
            sede_id=sede_id,
            activo=True,
            creado_por=creado_por,
        )
        
        # Persistir
        return await self.tipo_evento_repo.crear(tipo)
    
    @staticmethod
    def _validar_color_hex(color: str) -> bool:
        """Valida formato hexadecimal #RRGGBB"""
        import re
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))
