# app/kernel/application/ia/consultar_ia.py

from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.kernel.domain.ia import (
    IAConsulta,
    IAProviderPort,
    IAConsultasRepositoryPort,
    LimiteTokensExcedido,
    CostoExcesivo,
    PromptConDatosSensibles,
)
from app.infrastructure.db.repositories.ia import IAConsultasRepository


class ConsultarIADTO(BaseModel):
    """DTO para realizar una consulta a IA."""
    usuario_id: Optional[int] = Field(None, gt=0)
    sede_id: Optional[int] = Field(None, gt=0)

    proveedor: str = Field(..., min_length=1, max_length=50)
    modelo: Optional[str] = Field(None, max_length=100)

    prompt: str = Field(..., min_length=1)
    prompt_sanitizado: Optional[str] = None
    tiene_datos_sensibles: bool = False

    categoria: Optional[str] = Field(None, max_length=50)
    contexto: Optional[Dict[str, Any]] = None

    temperatura: float = Field(default=0.7, ge=0, le=1)
    max_tokens: Optional[int] = Field(None, gt=0)

    # Límites de seguridad opcionales
    max_tokens_permitidos: Optional[int] = Field(None, gt=0)
    max_costo_usd: Optional[float] = Field(None, gt=0)


class ConsultarIAResponse(BaseModel):
    """Respuesta de una consulta IA."""
    consulta: IAConsulta
    metadata_proveedor: Dict[str, Any]


class ConsultarIACU:
    """
    Caso de Uso: Consultar IA (proveedor agnóstico).
    
    Orquesta:
    - Valida prompt (datos sensibles, límites).
    - Llama al proveedor IA (MCP).
    - Registra la consulta en la BD.
    - Retorna entidad de dominio IAConsulta.
    """

    def __init__(
        self,
        repo: IAConsultasRepository,
        provider: IAProviderPort,
    ):
        self.repo = repo
        self.provider = provider

    async def ejecutar(self, dto: ConsultarIADTO) -> ConsultarIAResponse:
        # Validar datos sensibles (si la capa previa ya detectó)
        if dto.tiene_datos_sensibles and dto.prompt_sanitizado is None:
            raise PromptConDatosSensibles()

        # Determinar prompt que se enviará al proveedor
        prompt_enviado = dto.prompt_sanitizado or dto.prompt

        # Llamar proveedor IA
        inicio = datetime.utcnow()
        result = await self.provider.consultar(
            prompt=prompt_enviado,
            modelo=dto.modelo,
            temperatura=dto.temperatura,
            max_tokens=dto.max_tokens,
            contexto=dto.contexto,
        )
        fin = datetime.utcnow()

        # Extraer datos del resultado MCP estándar
        respuesta: str = result.get("respuesta", "")
        tokens_prompt: Optional[int] = result.get("tokens_prompt")
        tokens_respuesta: Optional[int] = result.get("tokens_respuesta")
        tokens_total: Optional[int] = result.get("tokens_total")
        modelo_usado: str = result.get("modelo_usado", dto.modelo or "")
        costo_usd: Optional[float] = result.get("costo_usd")

        # Validar límites de tokens si se configuró
        if dto.max_tokens_permitidos is not None and tokens_total is not None:
            if tokens_total > dto.max_tokens_permitidos:
                raise LimiteTokensExcedido(
                    tokens_solicitados=tokens_total,
                    limite=dto.max_tokens_permitidos,
                )

        # Validar límite de costo si se configuró
        if dto.max_costo_usd is not None and costo_usd is not None:
            if costo_usd > dto.max_costo_usd:
                raise CostoExcesivo(
                    costo_usd=costo_usd,
                    limite_usd=dto.max_costo_usd,
                )

        duracion = int((fin - inicio).total_seconds())

        # Registrar en infraestructura
        model = await self.repo.registrar(
            usuario_id=dto.usuario_id,
            sede_id=dto.sede_id,
            proveedor=dto.proveedor.lower(),
            modelo=modelo_usado,
            prompt=dto.prompt,
            prompt_sanitizado=dto.prompt_sanitizado,
            respuesta=respuesta,
            tokens_prompt=tokens_prompt,
            tokens_respuesta=tokens_respuesta,
            tokens_total=tokens_total,
            costo_usd=str(costo_usd) if costo_usd is not None else None,
            categoria=dto.categoria,
            contexto=dto.contexto,
            exitoso=True,
            mensaje_error=None,
            duracion_segundos=duracion,
            tiene_datos_sensibles=dto.tiene_datos_sensibles,
        )

        entidad = IAConsulta.model_validate(model)

        metadata = {
            "proveedor": dto.proveedor.lower(),
            "modelo_usado": modelo_usado,
            "tokens_prompt": tokens_prompt,
            "tokens_respuesta": tokens_respuesta,
            "tokens_total": tokens_total,
            "costo_usd": costo_usd,
            "duracion_segundos": duracion,
        }

        return ConsultarIAResponse(consulta=entidad, metadata_proveedor=metadata)
