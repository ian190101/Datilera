from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

# --- AGREGAR ESTA CLASE (DTO) ---
class CrearNotificacionInput(BaseModel):
    """Modelo de datos para enviar una notificación genérica."""
    usuario_id: int
    titulo: str
    mensaje: str
    data: Optional[Dict[str, Any]] = None
    tipo: str = "general"


# --- INTERFAZ DEL SERVICIO ---
class AbstractNotificacionesService(ABC):
    """
    Puerto (Interfaz) para el servicio de notificaciones.
    Define los métodos que el Dominio de Portafolio necesita llamar.
    """

    @abstractmethod
    async def notificar_nuevo_reporte(self, reporte_id: int, tutor_ids: List[int]) -> None:
        """Notifica a los tutores que se ha creado/enviado un nuevo reporte diario."""
        ...
    
    # Es posible que tu código también requiera un método genérico como este.
    # Si no lo usas, no hace daño dejarlo definido como abstracto o pasarlo.
    @abstractmethod
    async def enviar_notificacion(self, input_data: CrearNotificacionInput) -> None:
        ...