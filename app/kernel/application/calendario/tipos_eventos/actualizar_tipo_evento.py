# app/kernel/application/calendario/tipos_eventos/actualizar_tipo_evento.py

from typing import Optional

from app.kernel.domain.calendario import (
    TipoEvento,
    TipoEventoRepositoryPort,
    TipoEventoNoEncontradoError,
    CalendarioColorInvalidoError,
)


class ActualizarTipoEventoUseCase:
    """Caso de uso: Actualizar tipo de evento (US-CAL-001).
    
    Reglas:
    - Solo directora/admin/superadmin pueden actualizar
    - No se puede cambiar la sede
    """
    
    def __init__(self, tipo_evento_repo: TipoEventoRepositoryPort):
        self.tipo_evento_repo = tipo_evento_repo
    
    async def ejecutar(
        self,
        tipo_id: int,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        color: Optional[str] = None,
        icono: Optional[str] = None,
        requiere_aprobacion: Optional[bool] = None,
        visible_profesoras: Optional[bool] = None,
        visible_tutores: Optional[bool] = None,
    ) -> TipoEvento:
        """Actualiza un tipo de evento existente.
        
        Args:
            tipo_id: ID del tipo de evento
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripción (opcional)
            color: Nuevo color (opcional)
            icono: Nuevo ícono (opcional)
            requiere_aprobacion: Cambiar requisito de aprobación (opcional)
            visible_profesoras: Cambiar visibilidad profesoras (opcional)
            visible_tutores: Cambiar visibilidad tutores (opcional)
            
        Returns:
            TipoEvento actualizado
            
        Raises:
            TipoEventoNoEncontradoError: Si no existe
            CalendarioColorInvalidoError: Si el color no es válido
        """
        # Obtener tipo existente
        tipo = await self.tipo_evento_repo.obtener(tipo_id)
        if not tipo:
            raise TipoEventoNoEncontradoError(tipo_id=tipo_id)
        
        # Validar color si se proporciona
        if color and not self._validar_color_hex(color):
            raise CalendarioColorInvalidoError(color)
        
        # Actualizar campos
        if nombre is not None:
            tipo.nombre = nombre.strip()
        
        if descripcion is not None:
            tipo.descripcion = descripcion
        
        if color is not None:
            tipo.color = color
        
        if icono is not None:
            tipo.icono = icono
        
        if requiere_aprobacion is not None:
            tipo.requiere_aprobacion = requiere_aprobacion
        
        if visible_profesoras is not None:
            tipo.visible_profesoras = visible_profesoras
        
        if visible_tutores is not None:
            tipo.visible_tutores = visible_tutores
        
        # Persistir cambios
        return await self.tipo_evento_repo.actualizar(tipo)
    
    @staticmethod
    def _validar_color_hex(color: str) -> bool:
        """Valida formato hexadecimal #RRGGBB"""
        import re
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))
