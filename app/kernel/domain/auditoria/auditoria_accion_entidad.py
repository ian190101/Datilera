# app/kernel/domain/auditoria/auditoria_accion_entidad.py

"""
Entidad de Dominio: AuditoriaAccion
Representa un evento de auditoría en el sistema.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuditoriaAccion(BaseModel):
    """
    Entidad de dominio para auditoría de acciones.
    
    Inmutable: Los registros de auditoría nunca se modifican.
    """
    id: int = 0
    usuario_id: Optional[int] = None
    sede_id: Optional[int] = None
    
    # Datos básicos
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
    
    # Timestamp
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    
    # Nivel de severidad
    nivel: str = Field(default="info", max_length=20)
    
    # Método HTTP
    metodo_http: Optional[str] = Field(None, max_length=10)
    
    # Endpoint
    endpoint: Optional[str] = Field(None, max_length=255)
    
    # Código de respuesta HTTP
    codigo_respuesta: Optional[int] = None
    
    # Duración (ms)
    duracion_ms: Optional[int] = None
    
    # Descripción legible
    descripcion: Optional[str] = None
    
    # Tags
    tags: Optional[List[str]] = None
    
    # Contexto adicional
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
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
        frozen=False,  # Permitir modificación antes de persistir
    )
    
    @field_validator("nivel")
    @classmethod
    def validar_nivel(cls, v: str) -> str:
        """Valida que el nivel sea válido."""
        niveles_validos = {"debug", "info", "warning", "error", "critical"}
        if v not in niveles_validos:
            raise ValueError(f"Nivel debe ser uno de: {niveles_validos}")
        return v
    
    @field_validator("metodo_http")
    @classmethod
    def validar_metodo_http(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el método HTTP sea válido."""
        if v is None:
            return v
        metodos_validos = {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}
        if v.upper() not in metodos_validos:
            raise ValueError(f"Método HTTP debe ser uno de: {metodos_validos}")
        return v.upper()
    
    @field_validator("codigo_respuesta")
    @classmethod
    def validar_codigo_respuesta(cls, v: Optional[int]) -> Optional[int]:
        """Valida que el código de respuesta sea válido."""
        if v is None:
            return v
        if not (100 <= v <= 599):
            raise ValueError("Código de respuesta HTTP debe estar entre 100 y 599")
        return v
    
    def es_error(self) -> bool:
        """Verifica si el evento representa un error."""
        return not self.exitoso or self.nivel in {"error", "critical"}
    
    def es_critico(self) -> bool:
        """Verifica si el evento es crítico."""
        return self.nivel == "critical"
    
    def tiene_datos_sensibles(self) -> bool:
        """Verifica si el evento podría contener datos sensibles."""
        if self.datos_antes or self.datos_despues:
            return True
        return False
