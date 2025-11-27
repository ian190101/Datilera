# app/kernel/domain/auditoria/errors.py

"""
Excepciones del Dominio de Auditoría.

Define errores específicos del contexto de auditoría.
"""


# ===========================================================================
# Excepción Base
# ===========================================================================

class AuditoriaError(Exception):
    """Excepción base para errores de auditoría."""
    
    def __init__(self, mensaje: str, codigo: str = "AUDITORIA_ERROR"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(self.mensaje)


# ===========================================================================
# Errores de Auditoría de Acciones
# ===========================================================================

class AccionAuditoriaNoEncontrada(AuditoriaError):
    """Se lanza cuando no se encuentra una acción de auditoría."""
    
    def __init__(self, auditoria_id: int):
        super().__init__(
            mensaje=f"Acción de auditoría con ID {auditoria_id} no encontrada.",
            codigo="ACCION_AUDITORIA_NO_ENCONTRADA"
        )
        self.auditoria_id = auditoria_id


class NivelAuditoriaInvalido(AuditoriaError):
    """Se lanza cuando el nivel de auditoría es inválido."""
    
    def __init__(self, nivel: str):
        niveles_validos = ["debug", "info", "warning", "error", "critical"]
        super().__init__(
            mensaje=f"Nivel '{nivel}' inválido. Debe ser uno de: {niveles_validos}",
            codigo="NIVEL_AUDITORIA_INVALIDO"
        )
        self.nivel = nivel


class EntidadAuditoriaInvalida(AuditoriaError):
    """Se lanza cuando la entidad auditada es inválida."""
    
    def __init__(self, entidad: str):
        super().__init__(
            mensaje=f"Entidad '{entidad}' no es válida para auditoría.",
            codigo="ENTIDAD_AUDITORIA_INVALIDA"
        )
        self.entidad = entidad


class AccionAuditoriaInvalida(AuditoriaError):
    """Se lanza cuando la acción auditada es inválida."""
    
    def __init__(self, accion: str):
        super().__init__(
            mensaje=f"Acción '{accion}' no es válida para auditoría.",
            codigo="ACCION_AUDITORIA_INVALIDA"
        )
        self.accion = accion


# ===========================================================================
# Errores de Auditoría de Sesiones
# ===========================================================================

class SesionAuditoriaNoEncontrada(AuditoriaError):
    """Se lanza cuando no se encuentra una sesión auditada."""
    
    def __init__(self, sesion_id: int):
        super().__init__(
            mensaje=f"Sesión con ID {sesion_id} no encontrada en auditoría.",
            codigo="SESION_AUDITORIA_NO_ENCONTRADA"
        )
        self.sesion_id = sesion_id


class SesionYaCerrada(AuditoriaError):
    """Se lanza cuando se intenta operar sobre una sesión ya cerrada."""
    
    def __init__(self, sesion_id: int):
        super().__init__(
            mensaje=f"La sesión {sesion_id} ya está cerrada.",
            codigo="SESION_YA_CERRADA"
        )
        self.sesion_id = sesion_id


class SesionInactiva(AuditoriaError):
    """Se lanza cuando una sesión está inactiva por timeout."""
    
    def __init__(self, sesion_id: int, timeout_minutos: int):
        super().__init__(
            mensaje=f"La sesión {sesion_id} está inactiva (sin actividad por más de {timeout_minutos} minutos).",
            codigo="SESION_INACTIVA"
        )
        self.sesion_id = sesion_id
        self.timeout_minutos = timeout_minutos


class DispositivoTipoInvalido(AuditoriaError):
    """Se lanza cuando el tipo de dispositivo es inválido."""
    
    def __init__(self, dispositivo_tipo: str):
        tipos_validos = ["web", "mobile", "tablet", "desktop"]
        super().__init__(
            mensaje=f"Tipo de dispositivo '{dispositivo_tipo}' inválido. Debe ser uno de: {tipos_validos}",
            codigo="DISPOSITIVO_TIPO_INVALIDO"
        )
        self.dispositivo_tipo = dispositivo_tipo


class RazonCierreInvalida(AuditoriaError):
    """Se lanza cuando la razón de cierre de sesión es inválida."""
    
    def __init__(self, razon: str):
        razones_validas = ["logout_manual", "timeout", "forzado_admin", "token_expirado", "sesion_duplicada"]
        super().__init__(
            mensaje=f"Razón de cierre '{razon}' inválida. Debe ser una de: {razones_validas}",
            codigo="RAZON_CIERRE_INVALIDA"
        )
        self.razon = razon


# ===========================================================================
# Errores de Auditoría de Cambios
# ===========================================================================

class CambioAuditoriaNoEncontrado(AuditoriaError):
    """Se lanza cuando no se encuentra un cambio auditado."""
    
    def __init__(self, cambio_id: int):
        super().__init__(
            mensaje=f"Cambio de auditoría con ID {cambio_id} no encontrado.",
            codigo="CAMBIO_AUDITORIA_NO_ENCONTRADO"
        )
        self.cambio_id = cambio_id


class TipoDatoInvalido(AuditoriaError):
    """Se lanza cuando el tipo de dato de un cambio es inválido."""
    
    def __init__(self, tipo_dato: str):
        tipos_validos = ["string", "number", "boolean", "date", "datetime", "json", "array"]
        super().__init__(
            mensaje=f"Tipo de dato '{tipo_dato}' inválido. Debe ser uno de: {tipos_validos}",
            codigo="TIPO_DATO_INVALIDO"
        )
        self.tipo_dato = tipo_dato


class CampoSinCambios(AuditoriaError):
    """Se lanza cuando se intenta auditar un campo que no cambió."""
    
    def __init__(self, campo: str):
        super().__init__(
            mensaje=f"El campo '{campo}' no tiene cambios (valor anterior igual al nuevo).",
            codigo="CAMPO_SIN_CAMBIOS"
        )
        self.campo = campo


# ===========================================================================
# Errores de Auditoría de Exportaciones
# ===========================================================================

class ExportacionAuditoriaNoEncontrada(AuditoriaError):
    """Se lanza cuando no se encuentra una exportación auditada."""
    
    def __init__(self, exportacion_id: int):
        super().__init__(
            mensaje=f"Exportación con ID {exportacion_id} no encontrada en auditoría.",
            codigo="EXPORTACION_AUDITORIA_NO_ENCONTRADA"
        )
        self.exportacion_id = exportacion_id


class TipoExportacionInvalido(AuditoriaError):
    """Se lanza cuando el tipo de exportación es inválido."""
    
    def __init__(self, tipo: str):
        tipos_validos = ["pagos", "alumnos", "inventario", "reportes", "arqueo", "asistencias", "mensualidades", "cursos_extra", "profesoras"]
        super().__init__(
            mensaje=f"Tipo de exportación '{tipo}' inválido. Debe ser uno de: {tipos_validos}",
            codigo="TIPO_EXPORTACION_INVALIDO"
        )
        self.tipo = tipo


class FormatoExportacionInvalido(AuditoriaError):
    """Se lanza cuando el formato de exportación es inválido."""
    
    def __init__(self, formato: str):
        formatos_validos = ["excel", "pdf", "csv"]
        super().__init__(
            mensaje=f"Formato de exportación '{formato}' inválido. Debe ser uno de: {formatos_validos}",
            codigo="FORMATO_EXPORTACION_INVALIDO"
        )
        self.formato = formato


class ExportacionMasivaSospechosa(AuditoriaError):
    """Se lanza cuando se detecta una exportación masiva sospechosa."""
    
    def __init__(self, usuario_id: int, total_registros: int, umbral: int):
        super().__init__(
            mensaje=f"Exportación masiva sospechosa detectada: usuario {usuario_id} exportó {total_registros} registros (umbral: {umbral}).",
            codigo="EXPORTACION_MASIVA_SOSPECHOSA"
        )
        self.usuario_id = usuario_id
        self.total_registros = total_registros
        self.umbral = umbral


class ExportacionYaDescargada(AuditoriaError):
    """Se lanza cuando se intenta marcar como descargada una exportación ya descargada."""
    
    def __init__(self, exportacion_id: int):
        super().__init__(
            mensaje=f"La exportación {exportacion_id} ya fue descargada.",
            codigo="EXPORTACION_YA_DESCARGADA"
        )
        self.exportacion_id = exportacion_id


# ===========================================================================
# Errores de Auditoría de Prompts IA
# ===========================================================================

class PromptIAAuditoriaNoEncontrado(AuditoriaError):
    """Se lanza cuando no se encuentra un prompt IA auditado."""
    
    def __init__(self, prompt_id: int):
        super().__init__(
            mensaje=f"Prompt IA con ID {prompt_id} no encontrado en auditoría.",
            codigo="PROMPT_IA_AUDITORIA_NO_ENCONTRADO"
        )
        self.prompt_id = prompt_id


class CategoriaIAInvalida(AuditoriaError):
    """Se lanza cuando la categoría de prompt IA es inválida."""
    
    def __init__(self, categoria: str):
        categorias_validas = ["reporte", "busqueda", "estadistica", "ayuda", "analisis", "prediccion", "consulta"]
        super().__init__(
            mensaje=f"Categoría IA '{categoria}' inválida. Debe ser una de: {categorias_validas}",
            codigo="CATEGORIA_IA_INVALIDA"
        )
        self.categoria = categoria


class PromptConDatosSensibles(AuditoriaError):
    """Se lanza cuando un prompt contiene datos sensibles."""
    
    def __init__(self, prompt_id: int):
        super().__init__(
            mensaje=f"El prompt {prompt_id} contiene datos sensibles y requiere sanitización.",
            codigo="PROMPT_CON_DATOS_SENSIBLES"
        )
        self.prompt_id = prompt_id


class LimiteTokensExcedido(AuditoriaError):
    """Se lanza cuando se excede el límite de tokens para consultas IA."""
    
    def __init__(self, tokens_solicitados: int, limite: int):
        super().__init__(
            mensaje=f"Límite de tokens excedido: se solicitaron {tokens_solicitados} tokens (límite: {limite}).",
            codigo="LIMITE_TOKENS_EXCEDIDO"
        )
        self.tokens_solicitados = tokens_solicitados
        self.limite = limite


class CostoIAExcesivo(AuditoriaError):
    """Se lanza cuando el costo de una consulta IA es excesivo."""
    
    def __init__(self, costo_usd: float, limite_usd: float):
        super().__init__(
            mensaje=f"Costo excesivo: ${costo_usd:.4f} USD (límite: ${limite_usd:.4f} USD).",
            codigo="COSTO_IA_EXCESIVO"
        )
        self.costo_usd = costo_usd
        self.limite_usd = limite_usd


class ModeloIANoDisponible(AuditoriaError):
    """Se lanza cuando un modelo de IA no está disponible."""
    
    def __init__(self, modelo: str):
        super().__init__(
            mensaje=f"El modelo de IA '{modelo}' no está disponible o no es válido.",
            codigo="MODELO_IA_NO_DISPONIBLE"
        )
        self.modelo = modelo


# ===========================================================================
# Errores de Validación
# ===========================================================================

class CodigoRespuestaInvalido(AuditoriaError):
    """Se lanza cuando el código de respuesta HTTP es inválido."""
    
    def __init__(self, codigo: int):
        super().__init__(
            mensaje=f"Código de respuesta HTTP {codigo} inválido (debe estar entre 100 y 599).",
            codigo="CODIGO_RESPUESTA_INVALIDO"
        )
        self.codigo_respuesta = codigo


class MetodoHTTPInvalido(AuditoriaError):
    """Se lanza cuando el método HTTP es inválido."""
    
    def __init__(self, metodo: str):
        metodos_validos = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
        super().__init__(
            mensaje=f"Método HTTP '{metodo}' inválido. Debe ser uno de: {metodos_validos}",
            codigo="METODO_HTTP_INVALIDO"
        )
        self.metodo = metodo


class DuracionNegativa(AuditoriaError):
    """Se lanza cuando la duración es negativa."""
    
    def __init__(self, duracion: int):
        super().__init__(
            mensaje=f"Duración negativa no permitida: {duracion}",
            codigo="DURACION_NEGATIVA"
        )
        self.duracion = duracion
