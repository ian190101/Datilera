from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

# Límite recomendado para ahorrar tokens (ajustable según política)
MAX_PROMPT_CHARS_DEFAULT = 2000


@dataclass(frozen=True)
class PromptIA:
    """
    Objeto de valor del prompt de consulta a IA.

    Reglas:
    - Texto obligatorio, recortado (strip).
    - Longitud máxima configurable (por defecto 2000 chars) para ahorrar tokens.
    - Puede recibir un prefijo de sistema ya procesado fuera del dominio si aplica.

    Nota: Cualquier anonimización/mascarado sensible debe realizarse en
    capa de aplicación antes de instanciar este VO.
    """
    texto: str
    max_chars: int = MAX_PROMPT_CHARS_DEFAULT

    def __post_init__(self):
        t = (self.texto or "").strip()
        if not t:
            raise ValueError("El prompt (pregunta) no puede estar vacío.")
        if len(t) > self.max_chars:
            raise ValueError(f"El prompt excede el máximo de {self.max_chars} caracteres.")
        object.__setattr__(self, "texto", t)

    def preview(self, n: int = 120) -> str:
        """Devuelve un resumen corto del prompt para auditoría."""
        t = self.texto
        return t if len(t) <= n else t[:n].rstrip() + "…"