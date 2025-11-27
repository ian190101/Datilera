# app/kernel/domain/inscripcion/ports.py
"""
Puertos (interfaces) para el módulo de Inscripción.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional, Dict, Tuple

from .firma_entidad import Firma, TipoFirmante
from .formulario_inscripcion_entidad import FormularioInscripcion, EstadoFormulario
from .formulario_respuesta_entidad import FormularioRespuesta
from .documento_inscripcion_entidad import DocumentoInscripcion, EstadoProcesamientoDocumento
from .contrato_entidad import Contrato

# ==========================
# Repositorio: Formulario
# ==========================
class FormularioInscripcionRepositoryPort(ABC):
    @abstractmethod
    async def crear(self, alumno_id: int, sede_id: int, gestion: int) -> FormularioInscripcion:
        """Crea un formulario en estado BORRADOR."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_id(self, formulario_id: int) -> Optional[FormularioInscripcion]:
        """Obtiene formulario por ID."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_alumno(self, alumno_id: int, gestion: Optional[int] = None) -> List[FormularioInscripcion]:
        """Lista formularios por alumno (opcional filtrar por gestión)."""
        raise NotImplementedError

    @abstractmethod
    async def guardar(self, formulario: FormularioInscripcion) -> FormularioInscripcion:
        """Persiste cambios del formulario."""
        raise NotImplementedError

    @abstractmethod
    async def cambiar_estado(self, formulario_id: int, nuevo_estado: EstadoFormulario) -> None:
        """Actualiza el estado del formulario."""
        raise NotImplementedError

    @abstractmethod
    async def marcar_revisado(self, formulario_id: int, usuario_id: int) -> None:
        """Marca revisión con usuario y timestamp."""
        raise NotImplementedError

    @abstractmethod
    async def marcar_aprobado(self, formulario_id: int, usuario_id: int) -> None:
        """Aprueba el formulario y sella timestamp."""
        raise NotImplementedError

    @abstractmethod
    async def fijar_turno(self, formulario_id: int, turno_id: int) -> None:
        """Asigna turno al formulario."""
        raise NotImplementedError

# ==========================
# Repositorio: Respuestas
# ==========================
class FormularioRespuestaRepositoryPort(ABC):
    @abstractmethod
    async def upsert_seccion(self, formulario_id: int, seccion: str, datos: Dict[str, object]) -> None:
        """Guarda respuestas de una sección (reemplaza la sección)."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_formulario(self, formulario_id: int) -> List[FormularioRespuesta]:
        """Lista todas las respuestas del formulario."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_seccion(self, formulario_id: int, seccion: str) -> List[FormularioRespuesta]:
        """Lista respuestas de una sección."""
        raise NotImplementedError

    @abstractmethod
    async def eliminar_seccion(self, formulario_id: int, seccion: str) -> None:
        """Elimina todas las respuestas de una sección."""
        raise NotImplementedError

# ==========================
# Repositorio: Documentos
# ==========================
class DocumentoInscripcionRepositoryPort(ABC):
    @abstractmethod
    async def crear(self, doc: DocumentoInscripcion) -> DocumentoInscripcion:
        """Crea un documento en estado PENDIENTE."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_id(self, doc_id: int) -> Optional[DocumentoInscripcion]:
        """Obtiene documento por ID."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_formulario(self, formulario_id: int) -> List[DocumentoInscripcion]:
        """Lista documentos del formulario."""
        raise NotImplementedError

    @abstractmethod
    async def actualizar_estado(
        self, doc_id: int, estado: EstadoProcesamientoDocumento, error: Optional[str] = None, watermark_url: Optional[str] = None
    ) -> None:
        """Actualiza estado del pipeline (y watermark_url/error)."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_hash(self, hash_archivo: str) -> Optional[DocumentoInscripcion]:
        """Busca duplicados por hash para idempotencia."""
        raise NotImplementedError

    @abstractmethod
    async def listar_pendientes(self, limit: int = 100) -> List[DocumentoInscripcion]:
        """Lista documentos en estado PENDIENTE para procesamiento asíncrono."""
        raise NotImplementedError

    @abstractmethod
    async def actualizar_metadata(self, doc_id: int, mime: Optional[str], tamano_bytes: Optional[int], hash_archivo: Optional[str]) -> None:
        """Actualiza metadatos del archivo (mime, tamaño, hash)."""
        raise NotImplementedError

# ==========================
# Repositorio: Firmas
# ==========================
class FirmaRepositoryPort(ABC):
    @abstractmethod
    async def crear(self, firma: Firma) -> Firma:
        """Crea una firma."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_formulario_y_tipo(self, formulario_id: int, tipo: TipoFirmante) -> Optional[Firma]:
        """Obtiene firma por tipo para el formulario."""
        raise NotImplementedError

    @abstractmethod
    async def reemplazar(self, firma: Firma) -> Firma:
        """Reemplaza firma del mismo tipo (idempotencia por rol)."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_formulario(self, formulario_id: int) -> List[Firma]:
        """Lista firmas del formulario."""
        raise NotImplementedError

# ==========================
# Repositorio: Contratos
# ==========================
class ContratoRepositoryPort(ABC):
    @abstractmethod
    async def reservar_numeracion(self, sede_id: int) -> int:
        """Reserva numeración consecutiva por sede (transaccional)."""
        raise NotImplementedError

    @abstractmethod
    async def crear(self, contrato: Contrato) -> Contrato:
        """Crea el contrato con numeración y variables."""
        raise NotImplementedError

    @abstractmethod
    async def obtener_por_formulario(self, formulario_id: int) -> Optional[Contrato]:
        """Obtiene contrato por formulario."""
        raise NotImplementedError

    @abstractmethod
    async def actualizar_pdf_url(self, contrato_id: int, pdf_url: str) -> None:
        """Guarda la URL del PDF generado."""
        raise NotImplementedError

# ==========================
# Servicios externos (puertos)
# ==========================
class WatermarkServicePort(ABC):
    @abstractmethod
    async def encolar_marca_agua(self, documento_id: int) -> None:
        """Encola el procesamiento de marca de agua para un documento."""
        raise NotImplementedError

class PdfGeneratorServicePort(ABC):
    @abstractmethod
    async def generar_contrato_pdf(self, contrato_id: int, plantilla_version: Optional[int], variables: Dict[str, object]) -> str:
        """
        Genera el PDF del contrato y devuelve la URL local donde quedó almacenado.
        """
        raise NotImplementedError

class CodigoAccesoServicePort(ABC):
    @abstractmethod
    async def validar_y_consumir(self, codigo: str, alumno_id: int, sede_id: int) -> bool:
        """
        Valida el código de acceso de 6 caracteres y lo consume si es válido (flujo Acceso).
        """
        raise NotImplementedError
