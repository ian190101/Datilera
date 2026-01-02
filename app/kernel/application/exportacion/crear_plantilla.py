# app/kernel/application/exportacion/crear_plantilla.py

from __future__ import annotations
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from app.kernel.domain.exportacion import (
    AbstractPlantillaExportacionRepository,
    PlantillaExportacion,
    TipoReporte,
    FormatoArchivo,
    PlantillaDuplicadaError,
)


class CrearPlantillaIn(BaseModel):
    """Input para crear plantilla."""
    nombre: str = Field(min_length=3, max_length=150)
    descripcion: Optional[str] = None
    tipo_reporte: TipoReporte
    formato_default: FormatoArchivo
    columnas_incluidas: list[str] = Field(min_length=1)
    filtros_default: Optional[Dict[str, Any]] = None
    es_publica: bool = Field(default=True)


class CrearPlantillaOut(BaseModel):
    """Output con plantilla creada."""
    plantilla: PlantillaExportacion
    mensaje: str


class CrearPlantillaCU:
    """
    Caso de uso: Crear plantilla reutilizable de exportación.
    
    Útil para:
    - Exportaciones recurrentes (reporte mensual de pagos)
    - Configuraciones compartidas entre usuarios
    - Plantillas estándar del sistema
    
    Validaciones:
    - Nombre único (no puede duplicarse)
    - Al menos una columna debe incluirse
    """
    
    def __init__(
        self,
        plantilla_repo: AbstractPlantillaExportacionRepository,
        usuario_id: int,
    ) -> None:
        self._repo = plantilla_repo
        self._usuario_id = usuario_id
    
    async def __call__(
        self,
        data: CrearPlantillaIn,
    ) -> CrearPlantillaOut:
        """Crea una nueva plantilla."""
        
        # Verificar que no exista plantilla con ese nombre
        plantilla_existente = await self._repo.obtener_por_nombre(data.nombre)
        
        if plantilla_existente:
            raise PlantillaDuplicadaError(data.nombre)
        
        # Crear plantilla
        plantilla = await self._repo.crear_plantilla(
            nombre=data.nombre,
            descripcion=data.descripcion,
            tipo_reporte=data.tipo_reporte,
            formato_default=data.formato_default,
            columnas_incluidas=data.columnas_incluidas,
            filtros_default=data.filtros_default,
            creado_por=self._usuario_id,
            es_publica=data.es_publica,
        )
        
        visibilidad = "pública" if data.es_publica else "privada"
        
        return CrearPlantillaOut(
            plantilla=plantilla,
            mensaje=f"Plantilla '{plantilla.nombre}' creada como {visibilidad}",
        )
