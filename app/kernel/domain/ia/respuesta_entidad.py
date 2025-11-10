from __future__ import annotations
from dataclasses import dataclass

# Límite recomendado por claridad de auditoría (puede ajustarse en app)
MAX_RESPUESTA_CHARS_DEFAULT = 10000


@dataclass(frozen=True)
class RespuestaIA:
    """
    Objeto de valor de la respuesta de IA.

    Reglas:
    - Texto obligatorio.
    - Longitud máxima configurable para evitar registros desmesurados.
    """
    texto: str
    max_chars: int = MAX_RESPUESTA_CHARS_DEFAULT

    def __post_init__(self):
        t = (self.texto or "").strip()
        if not t:
            raise ValueError("La respuesta de IA no puede estar vacía.")
        if len(t) > self.max_chars:
            raise ValueError(f"La respuesta excede el máximo de {self.max_chars} caracteres.")
        object.__setattr__(self, "texto", t)