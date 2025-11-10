from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .prompt_entidad import PromptIA
from .respuesta_entidad import RespuestaIA


@dataclass
class IAConsulta:
    """
    Entidad **IAConsulta** (registro/auditoría de interacción con IA).

    Mapea a infraestructura: `ia_consultas` con columnas:
    - id (PK)
    - usuario_id (FK usuarios.id)
    - pregunta (Text)        -> PromptIA.texto
    - respuesta (Text)       -> RespuestaIA.texto
    - tokens_consumidos (Int)
    - creado_en (DateTime)

    Reglas:
    - `usuario_id` requerido.
    - `tokens_consumidos` >= 0.
    - pregunta/respuesta no vacías (validado en VO).
    - Sin dependencias de proveedores (OpenAI/DeepSeek/etc.): esto es puro dominio/auditoría.

    Historias relacionadas (documento):
    - Solo ciertos roles pueden usar IA (policy en aplicación).
    - Minimizar tokens: controlar longitud del prompt/respuesta (VOs).
    - Registrar auditoría de prompts/respuestas y tokens consumidos.
    """
    id: int
    usuario_id: int
    prompt: PromptIA
    respuesta: RespuestaIA
    tokens_consumidos: int = 0
    creado_en: datetime = None

    def __post_init__(self):
        if self.usuario_id <= 0:
            raise ValueError("usuario_id inválido.")
        if self.tokens_consumidos < 0:
            raise ValueError("tokens_consumidos no puede ser negativo.")
        self.creado_en = self.creado_en or datetime.utcnow()

    # --- Utilidades de dominio ---
    def resumen_auditoria(self, ancho: int = 60) -> str:
        """Resumen corto (pregunta/resp) útil para logs internos/alertas."""
        p = self.prompt.preview(ancho)
        r = (self.respuesta.texto if len(self.respuesta.texto) <= ancho
             else self.respuesta.texto[:ancho].rstrip() + "…")
        return f"Q: {p} | A: {r} | tokens={self.tokens_consumidos}"