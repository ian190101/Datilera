# app/kernel/domain/auditoria/auditoria_sesion_entidad.py

"""
Entidad de Dominio: AuditoriaSesion
Representa una sesión activa de usuario.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuditoriaSesion(BaseModel):
    """
    Entidad de dominio para tracking de sesiones.
    """
    id: int = 0
    sesion_id: int = Field(..., gt=0)
    usuario_id: int = Field(..., gt=0)
    sede_id: Optional[int] = None
    
    # Datos de conexión
    ip: Optional[str] = Field(None, max_length=50)
    user_agent: Optional[str] = Field(None, max_length=500)
    dispositivo_tipo: Optional[str] = Field(None, max_length=20)
    
    # Timestamps
    inicio_sesion: datetime = Field(default_factory=datetime.utcnow)
    ultimo_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    fin_sesion: Optional[datetime] = None
    
    # Estado
    activa: bool = True
    razon_cierre: Optional[str] = Field(None, max_length=50)
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        from_attributes=True,
        frozen=False,
    )
    
    @field_validator("dispositivo_tipo")
    @classmethod
    def validar_dispositivo_tipo(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el tipo de dispositivo sea válido."""
        if v is None:
            return v
        tipos_validos = {"web", "mobile", "tablet", "desktop"}
        if v.lower() not in tipos_validos:
            raise ValueError(f"Tipo de dispositivo debe ser uno de: {tipos_validos}")
        return v.lower()
    
    @field_validator("razon_cierre")
    @classmethod
    def validar_razon_cierre(cls, v: Optional[str]) -> Optional[str]:
        """Valida que la razón de cierre sea válida."""
        if v is None:
            return v
        razones_validas = {
            "logout_manual",
            "timeout",
            "forzado_admin",
            "token_expirado",
            "sesion_duplicada"
        }
        if v not in razones_validas:
            raise ValueError(f"Razón de cierre debe ser una de: {razones_validas}")
        return v
    
    def actualizar_heartbeat(self) -> None:
        """Actualiza el timestamp de última actividad."""
        self.ultimo_heartbeat = datetime.utcnow()
    
    def cerrar_sesion(self, razon: str = "logout_manual") -> None:
        """Cierra la sesión."""
        self.activa = False
        self.fin_sesion = datetime.utcnow()
        self.razon_cierre = razon
    
    def esta_inactiva(self, timeout_minutos: int = 30) -> bool:
        """Verifica si la sesión está inactiva."""
        if not self.activa:
            return True
        
        limite = datetime.utcnow() - timedelta(minutes=timeout_minutos)
        return self.ultimo_heartbeat < limite
    
    def duracion_segundos(self) -> Optional[int]:
        """Calcula la duración de la sesión en segundos."""
        if self.fin_sesion is None:
            # Sesión aún activa
            delta = datetime.utcnow() - self.inicio_sesion
        else:
            delta = self.fin_sesion - self.inicio_sesion
        
        return int(delta.total_seconds())
