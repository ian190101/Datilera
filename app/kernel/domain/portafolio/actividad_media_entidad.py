# app/kernel/dominio/portafolio/archivo_media_portafolio.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# 1. CORRECCIÓN: Debe coincidir con el Enum de la Base de Datos (actividad_media.py)
class TipoMedia(str, Enum):
    IMAGEN = "imagen"   # Antes tenías "foto" -> ERROR
    VIDEO = "video"
    AUDIO = "audio"     # Faltaba
    DOCUMENTO = "documento" # Faltaba


# Este Enum está bien, sirve para controlar la lógica de negocio del lado de la App
class EstadoMedia(str, Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    LISTO = "listo"
    ELIMINADO = "eliminado"


class ArchivoMediaPortafolio(BaseModel):
    """
    Entidad de dominio para un archivo multimedia del portafolio.
    Mapea a app.infrastructure.db.models.portafolio.ActividadMedia.
    """
    # Configuración Pydantic V2
    model_config = ConfigDict(from_attributes=True)

    id: int
    actividad_id: int
    tipo: TipoMedia
    
    # 2. CORRECCIÓN: En la BD se llama 'url', no 'url_original'
    url: str 
    
    url_marcada: Optional[str] = None
    
    # Nota: Si en la BD el estado es un string simple, Pydantic intentará convertirlo a este Enum.
    # Si la BD tiene un valor que no está aquí, fallará. Asegúrate que coincidan.
    estado: EstadoMedia 
    
    # 3. CORRECCIÓN: En la BD es 'creado_en'
    creado_en: datetime 
    
    fecha_descarga: Optional[datetime] = None
    fecha_eliminacion_programada: Optional[datetime] = None
    nombre_archivo: str
    mime: Optional[str] = None
    tamano_bytes: Optional[int] = None

    # --- PROPIEDAD CALCULADA ÚTIL ---
    @property
    def ha_expirado(self) -> bool:
        """Devuelve True si ya pasó la fecha de eliminación programada."""
        if not self.fecha_eliminacion_programada:
            return False
        return datetime.now() > self.fecha_eliminacion_programada


@dataclass
class PoliticaExpiracionMedia:
    """
    Value Object / Domain Service para la regla de borrado:
    borrar media 'dias_gracia' días después del día de la descarga.
    """

    dias_gracia: int = 3

    def calcular_fecha_eliminacion(self, fecha_descarga: datetime) -> datetime:
        return fecha_descarga + timedelta(days=self.dias_gracia)