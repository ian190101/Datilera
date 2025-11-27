# app/kernel/domain/ia/errors.py

"""
Excepciones del Dominio de IA.
"""


# ===========================================================================
# Excepción Base
# ===========================================================================

class IAError(Exception):
    """Excepción base para errores de IA."""
    
    def __init__(self, mensaje: str, codigo: str = "IA_ERROR"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(self.mensaje)


# ===========================================================================
# Errores de Consultas
# ===========================================================================

class ConsultaIANoEncontrada(IAError):
    """Se lanza cuando no se encuentra una consulta."""
    
    def __init__(self, consulta_id: int):
        super().__init__(
            mensaje=f"Consulta IA con ID {consulta_id} no encontrada.",
            codigo="CONSULTA_IA_NO_ENCONTRADA"
        )
        self.consulta_id = consulta_id


class ProveedorIANoDisponible(IAError):
    """Se lanza cuando un proveedor de IA no está disponible."""
    
    def __init__(self, proveedor: str):
        super().__init__(
            mensaje=f"El proveedor de IA '{proveedor}' no está disponible o no está configurado.",
            codigo="PROVEEDOR_IA_NO_DISPONIBLE"
        )
        self.proveedor = proveedor


class ModeloIANoDisponible(IAError):
    """Se lanza cuando un modelo de IA no está disponible."""
    
    def __init__(self, proveedor: str, modelo: str):
        super().__init__(
            mensaje=f"El modelo '{modelo}' no está disponible en el proveedor '{proveedor}'.",
            codigo="MODELO_IA_NO_DISPONIBLE"
        )
        self.proveedor = proveedor
        self.modelo = modelo


class ErrorConsultaIA(IAError):
    """Se lanza cuando hay un error al consultar a IA."""
    
    def __init__(self, proveedor: str, mensaje: str):
        super().__init__(
            mensaje=f"Error al consultar {proveedor}: {mensaje}",
            codigo="ERROR_CONSULTA_IA"
        )
        self.proveedor = proveedor


class LimiteTokensExcedido(IAError):
    """Se lanza cuando se excede el límite de tokens."""
    
    def __init__(self, tokens_solicitados: int, limite: int):
        super().__init__(
            mensaje=f"Límite de tokens excedido: {tokens_solicitados} > {limite}",
            codigo="LIMITE_TOKENS_EXCEDIDO"
        )
        self.tokens_solicitados = tokens_solicitados
        self.limite = limite


class CostoExcesivo(IAError):
    """Se lanza cuando el costo estimado es excesivo."""
    
    def __init__(self, costo_usd: float, limite_usd: float):
        super().__init__(
            mensaje=f"Costo excesivo: ${costo_usd:.4f} > ${limite_usd:.4f}",
            codigo="COSTO_EXCESIVO"
        )
        self.costo_usd = costo_usd
        self.limite_usd = limite_usd


class PromptConDatosSensibles(IAError):
    """Se lanza cuando un prompt contiene datos sensibles."""
    
    def __init__(self):
        super().__init__(
            mensaje="El prompt contiene datos sensibles y debe ser sanitizado antes de enviarlo.",
            codigo="PROMPT_CON_DATOS_SENSIBLES"
        )


class ConfiguracionIAInvalida(IAError):
    """Se lanza cuando la configuración de IA es inválida."""
    
    def __init__(self, detalle: str):
        super().__init__(
            mensaje=f"Configuración de IA inválida: {detalle}",
            codigo="CONFIGURACION_IA_INVALIDA"
        )


class APIKeyNoConfigurada(IAError):
    """Se lanza cuando la API key no está configurada."""
    
    def __init__(self, proveedor: str):
        super().__init__(
            mensaje=f"API key para el proveedor '{proveedor}' no está configurada en las variables de entorno.",
            codigo="API_KEY_NO_CONFIGURADA"
        )
        self.proveedor = proveedor


class RateLimitExcedido(IAError):
    """Se lanza cuando se excede el rate limit del proveedor."""
    
    def __init__(self, proveedor: str, reintentar_en: int):
        super().__init__(
            mensaje=f"Rate limit excedido para {proveedor}. Reintentar en {reintentar_en} segundos.",
            codigo="RATE_LIMIT_EXCEDIDO"
        )
        self.proveedor = proveedor
        self.reintentar_en = reintentar_en
