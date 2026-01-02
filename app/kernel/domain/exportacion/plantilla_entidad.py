# app/kernel/domain/exportacion/plantilla_entidad.py

from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

from .exportacion_entidad import TipoReporte, FormatoArchivo
from .errors import PlantillaNoAccesibleError


class PlantillaExportacion(BaseModel):
    """
    Entidad de dominio para plantillas de exportación.
    Representa una configuración reutilizable de exportación.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nombre: str
    descripcion: Optional[str] = None
    
    tipo_reporte: TipoReporte
    formato_default: FormatoArchivo
    
    columnas_incluidas: List[str]
    filtros_default: Optional[Dict[str, Any]] = None
    
    creado_por: int
    creado_en: datetime
    
    es_publica: bool
    activa: bool
    
    # === REGLAS DE NEGOCIO ===
    
    @property
    def puede_usarse(self) -> bool:
        """Verifica si la plantilla puede usarse."""
        return self.activa
    
    def validar_uso(self, usuario_id: int) -> None:
        """
        Valida que el usuario pueda usar esta plantilla.
        """
        
        
        if not self.activa:
            raise PlantillaNoAccesibleError(
                self.id,
                "La plantilla está desactivada"
            )
        
        # Si no es pública, solo el creador puede usarla
        if not self.es_publica and self.creado_por != usuario_id:
            raise PlantillaNoAccesibleError(
                self.id,
                "No tiene permisos para usar esta plantilla privada"
            )
