# app/kernel/domain/exportacion/ports.py

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from .exportacion_entidad import Exportacion, TipoReporte, FormatoArchivo, EstadoExportacion
from .plantilla_entidad import PlantillaExportacion


class AbstractExportacionRepository(ABC):
    """Puerto para persistencia de exportaciones."""
    
    @abstractmethod
    async def crear_exportacion(
        self,
        usuario_id: int,
        sede_id: int,
        tipo_reporte: TipoReporte,
        formato: FormatoArchivo,
        filtros: Optional[Dict[str, Any]] = None,
        plantilla_id: Optional[int] = None,
    ) -> Exportacion:
        """Crea un nuevo registro de exportación."""
        ...
    
    @abstractmethod
    async def obtener_por_id(self, exportacion_id: int) -> Optional[Exportacion]:
        """Obtiene una exportación por ID."""
        ...
    
    @abstractmethod
    async def actualizar_estado(
        self,
        exportacion_id: int,
        estado: EstadoExportacion,
        url_descarga: Optional[str] = None,
        ruta_archivo: Optional[str] = None,
        tamano_bytes: Optional[int] = None,
        error_mensaje: Optional[str] = None,
        fecha_expiracion: Optional[date] = None,
    ) -> None:
        """Actualiza el estado de una exportación."""
        ...
    
    @abstractmethod
    async def listar_por_usuario(
        self,
        usuario_id: int,
        limite: int = 20,
    ) -> List[Exportacion]:
        """Lista exportaciones de un usuario."""
        ...
    
    @abstractmethod
    async def incrementar_descargas(self, exportacion_id: int) -> None:
        """Incrementa el contador de descargas."""
        ...
    
    @abstractmethod
    async def eliminar_exportacion(self, exportacion_id: int) -> None:
        """Elimina una exportación."""
        ...
    
    @abstractmethod
    async def listar_expiradas(self, fecha_limite: date) -> List[Exportacion]:
        """Lista exportaciones expiradas antes de una fecha."""
        ...


class AbstractPlantillaExportacionRepository(ABC):
    """Puerto para persistencia de plantillas de exportación."""
    
    @abstractmethod
    async def crear_plantilla(
        self,
        nombre: str,
        descripcion: Optional[str],
        tipo_reporte: TipoReporte,
        formato_default: FormatoArchivo,
        columnas_incluidas: List[str],
        filtros_default: Optional[Dict[str, Any]],
        creado_por: int,
        es_publica: bool = True,
    ) -> PlantillaExportacion:
        """Crea una nueva plantilla."""
        ...
    
    @abstractmethod
    async def obtener_por_id(self, plantilla_id: int) -> Optional[PlantillaExportacion]:
        """Obtiene una plantilla por ID."""
        ...
    
    @abstractmethod
    async def obtener_por_nombre(self, nombre: str) -> Optional[PlantillaExportacion]:
        """Obtiene una plantilla por nombre."""
        ...
    
    @abstractmethod
    async def listar_plantillas(
        self,
        tipo_reporte: Optional[TipoReporte] = None,
        solo_publicas: bool = True,
        usuario_id: Optional[int] = None,
    ) -> List[PlantillaExportacion]:
        """Lista plantillas según filtros."""
        ...
    
    @abstractmethod
    async def actualizar_plantilla(
        self,
        plantilla_id: int,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        columnas_incluidas: Optional[List[str]] = None,
        filtros_default: Optional[Dict[str, Any]] = None,
        es_publica: Optional[bool] = None,
    ) -> None:
        """Actualiza una plantilla existente."""
        ...
    
    @abstractmethod
    async def desactivar_plantilla(self, plantilla_id: int) -> None:
        """Desactiva una plantilla (soft delete)."""
        ...


class AbstractGeneradorArchivosService(ABC):
    """Puerto para servicios de generación de archivos."""
    
    @abstractmethod
    async def generar_pdf(
        self,
        tipo_reporte: TipoReporte,
        datos: Any,
        columnas: Optional[List[str]] = None,
    ) -> tuple[str, int]:
        """
        Genera un archivo PDF.
        
        Returns:
            tuple[ruta_archivo, tamano_bytes]
        """
        ...
    
    @abstractmethod
    async def generar_excel(
        self,
        tipo_reporte: TipoReporte,
        datos: Any,
        columnas: Optional[List[str]] = None,
    ) -> tuple[str, int]:
        """
        Genera un archivo Excel.
        
        Returns:
            tuple[ruta_archivo, tamano_bytes]
        """
        ...
    
    @abstractmethod
    async def generar_csv(
        self,
        tipo_reporte: TipoReporte,
        datos: Any,
        columnas: Optional[List[str]] = None,
    ) -> tuple[str, int]:
        """
        Genera un archivo CSV.
        
        Returns:
            tuple[ruta_archivo, tamano_bytes]
        """
        ...


class AbstractAlmacenamientoService(ABC):
    """Puerto para servicios de almacenamiento de archivos."""
    
    @abstractmethod
    async def guardar_archivo(
        self,
        ruta_origen: str,
        nombre_archivo: str,
    ) -> tuple[str, str]:
        """
        Guarda un archivo en almacenamiento.
        
        Returns:
            tuple[ruta_fisica, url_descarga]
        """
        ...
    
    @abstractmethod
    async def eliminar_archivo(self, ruta: str) -> None:
        """Elimina un archivo del almacenamiento."""
        ...
    
    @abstractmethod
    async def archivo_existe(self, ruta: str) -> bool:
        """Verifica si un archivo existe."""
        ...
