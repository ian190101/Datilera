# app/kernel/application/auditoria/auditoria_acciones/registrar_accion.py

"""
Caso de Uso: Registrar Acción de Auditoría
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field

from app.kernel.domain.auditoria import AuditoriaAccion
from app.infrastructure.db.repositories.auditoria import AuditoriaAccionesRepository


# ===== DTOs =====

class RegistrarAccionDTO(BaseModel):
    """DTO para registrar una acción de auditoría."""
    usuario_id: Optional[int] = None
    sede_id: Optional[int] = None
    entidad: str = Field(..., min_length=1, max_length=120)
    entidad_id: Optional[str] = Field(None, max_length=64)
    accion: str = Field(..., min_length=1, max_length=30)
    
    # Snapshots
    datos_antes: Optional[Dict[str, Any]] = None
    datos_despues: Optional[Dict[str, Any]] = None
    
    # Datos de conexión
    ip: Optional[str] = Field(None, max_length=50)
    user_agent: Optional[str] = None
    sesion_id: Optional[int] = None
    
    # Nivel de severidad
    nivel: str = Field(default="info", max_length=20)
    
    # Método HTTP
    metodo_http: Optional[str] = Field(None, max_length=10)
    
    # Endpoint
    endpoint: Optional[str] = Field(None, max_length=255)
    
    # Código de respuesta
    codigo_respuesta: Optional[int] = None
    
    # Duración
    duracion_ms: Optional[int] = None
    
    # Descripción
    descripcion: Optional[str] = None
    
    # Tags
    tags: Optional[List[str]] = None
    
    # Contexto
    contexto: Optional[Dict[str, Any]] = None
    
    # Éxito
    exitoso: bool = True
    
    # Error
    mensaje_error: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Dispositivo
    dispositivo_info: Optional[Dict[str, Any]] = None
    
    # Geolocalización
    geolocalizacion: Optional[Dict[str, Any]] = None


# ===== Caso de Uso =====

class RegistrarAccionCU:
    """
    Caso de Uso: Registrar Acción de Auditoría.
    
    Responsabilidad: Registrar eventos de auditoría en el sistema.
    """
    
    def __init__(self, repo: AuditoriaAccionesRepository):
        self.repo = repo
    
    async def ejecutar(self, dto: RegistrarAccionDTO) -> AuditoriaAccion:
        """
        Registra una acción de auditoría.
        
        Args:
            dto: Datos de la acción a registrar
            
        Returns:
            Entidad de dominio AuditoriaAccion con el registro creado
        """
        # Registrar en infraestructura (retorna modelo SQLAlchemy)
        model = await self.repo.registrar(
            usuario_id=dto.usuario_id,
            sede_id=dto.sede_id,
            entidad=dto.entidad,
            accion=dto.accion,
            entidad_id=dto.entidad_id,
            datos_antes=dto.datos_antes,
            datos_despues=dto.datos_despues,
            ip=dto.ip,
            user_agent=dto.user_agent,
            sesion_id=dto.sesion_id,
            nivel=dto.nivel,
            metodo_http=dto.metodo_http,
            endpoint=dto.endpoint,
            codigo_respuesta=dto.codigo_respuesta,
            duracion_ms=dto.duracion_ms,
            descripcion=dto.descripcion,
            tags=dto.tags,
            contexto=dto.contexto,
            exitoso=dto.exitoso,
            mensaje_error=dto.mensaje_error,
            stack_trace=dto.stack_trace,
            dispositivo_info=dto.dispositivo_info,
            geolocalizacion=dto.geolocalizacion,
        )
        
        # Mapear a entidad de dominio
        return AuditoriaAccion.model_validate(model)
