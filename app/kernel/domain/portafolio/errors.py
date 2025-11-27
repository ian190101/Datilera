# app/kernel/domain/portafolio/errors.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PortafolioError(Exception):
    """Error base para el dominio de Portafolio."""
    # Este SÍ se queda como dataclass para manejar los campos base
    code: int
    message: str
    detail: Optional[str] = None

    def __str__(self) -> str:
        if self.detail:
            return f"{self.code}: {self.message} ({self.detail})"
        return f"{self.code}: {self.message}"


# --- CORRECCIÓN: ELIMINAR @dataclass DE LAS CLASES HIJAS ---
# Al tener un __init__ manual y heredar de una dataclass con defaults,
# el decorador @dataclass causa conflictos de orden de argumentos.

class ReporteNoEncontradoError(PortafolioError):
    reporte_id: int

    def __init__(self, reporte_id: int) -> None:
        super().__init__(
            code=404,
            message="Reporte diario no encontrado",
            detail=f"ReporteDiario id={reporte_id}",
        )
        self.reporte_id = reporte_id


class ActividadNoEncontradaError(PortafolioError):
    actividad_id: int

    def __init__(self, actividad_id: int) -> None:
        super().__init__(
            code=404,
            message="Actividad de portafolio no encontrada",
            detail=f"Actividad id={actividad_id}",
        )
        self.actividad_id = actividad_id


class MediaNoEncontradaError(PortafolioError):
    media_id: int

    def __init__(self, media_id: int) -> None:
        super().__init__(
            code=404,
            message="Archivo multimedia no encontrado",
            detail=f"ArchivoMedia id={media_id}",
        )
        self.media_id = media_id


class MediaNoDisponibleError(PortafolioError):
    media_id: int

    def __init__(self, media_id: int) -> None:
        super().__init__(
            code=409,
            message="Archivo multimedia no disponible para descarga",
            detail=f"ArchivoMedia id={media_id}",
        )
        self.media_id = media_id


class MediaExpiradaError(PortafolioError):
    media_id: int

    def __init__(self, media_id: int) -> None:
        super().__init__(
            code=410,
            message="Archivo multimedia expirado y/o eliminado",
            detail=f"ArchivoMedia id={media_id}",
        )
        self.media_id = media_id