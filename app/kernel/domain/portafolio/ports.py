# app/kernel/domain/portafolio/puertos.py
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional, Dict

# Importamos los nombres CORRECTOS
from .reporte_diario_entidad import ReporteDiario
from .reporte_lectura_tutor_entidad import LecturaTutor
from .actividad_entidad import ActividadPortafolio
from .actividad_media_entidad import ArchivoMediaPortafolio


class AbstractReportesDiariosRepository(ABC):
    """Puerto para la persistencia de reportes diarios."""

    @abstractmethod
    async def crear_o_actualizar(
        self,
        alumno_id: int,
        profesora_id: int,
        fecha: date,
        contenido: Optional[str], # <--- CORREGIDO: Antes era 'resumen'
    ) -> ReporteDiario:
        ...

    @abstractmethod
    async def obtener_por_id(self, reporte_id: int) -> Optional[ReporteDiario]:
        ...

    @abstractmethod
    async def listar_por_alumno(
        self,
        alumno_id: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
    ) -> List[ReporteDiario]:
        ...
    
    # ... resto de métodos de reportes (marcar_enviado, etc) igual ...
    @abstractmethod
    async def marcar_enviado(self, reporte_id: int, enviado_en: datetime) -> None: ...
    @abstractmethod
    async def marcar_confirmado(self, reporte_id: int, confirmado_en: datetime) -> None: ...
    @abstractmethod
    async def listar_no_enviados_hasta_fecha(self, fecha: date) -> List[ReporteDiario]: ...


class AbstractReporteLecturasTutoresRepository(ABC):
    # Este estaba bien, solo verifica los imports
    @abstractmethod
    async def registrar_lectura(self, reporte_id: int, tutor_id: int) -> LecturaTutor: ...
    @abstractmethod
    async def listar_por_reporte(self, reporte_id: int) -> List[LecturaTutor]: ...


class AbstractActividadesRepository(ABC):
    """Puerto para actividades de Portafolio."""

    @abstractmethod
    async def crear(
        self,
        alumno_id: Optional[int],
        grupo_id: Optional[int],
        profesora_id: int,   # <--- FALTABA ESTO
        fecha: date,
        titulo: str,
        descripcion: Optional[str],
        # tipo: str,  <--- ELIMINADO (Ya no existe en DB)
    ) -> ActividadPortafolio:
        ...

    @abstractmethod
    async def obtener_por_id(self, actividad_id: int) -> Optional[ActividadPortafolio]:
        ...

    @abstractmethod
    async def listar_por_alumno(
        self,
        alumno_id: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
    ) -> List[ActividadPortafolio]:
        ...


class AbstractActividadMediaRepository(ABC):
    """Puerto para archivos multimedia asociados a actividades."""

    @abstractmethod
    async def crear(
        self,
        actividad_id: int,
        tipo: str,
        url: str,           # <--- CORREGIDO: Antes era url_original
        nombre_archivo: str,
        mime: Optional[str],
        tamano_bytes: Optional[int],
    ) -> ArchivoMediaPortafolio:
        ...

    # ... Resto de métodos (listar, contar, actualizar, registrar_descarga) igual ...
    @abstractmethod
    async def listar_por_actividad(self, actividad_id: int) -> List[ArchivoMediaPortafolio]: ...
    @abstractmethod
    async def contar_por_tipo(self, actividad_id: int) -> Dict[str, int]: ...
    @abstractmethod
    async def actualizar_estado_y_urls(self, media_id: int, estado: str, url_marcada: Optional[str] = None) -> None: ...
    @abstractmethod
    async def registrar_descarga(self, media_id: int, fecha_descarga: datetime, fecha_eliminacion_programada: datetime) -> None: ...
    @abstractmethod
    async def listar_para_borrado(self, ahora: datetime) -> List[ArchivoMediaPortafolio]: ...

class AbstractStorageService(ABC):
    @abstractmethod
    async def eliminar_archivo(self, path: str) -> None: ...