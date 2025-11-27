# app/kernel/domain/inscripcion/errors.py
"""
Excepciones de dominio para Inscripción.
"""

class InscripcionError(Exception):
    """Base de errores de Inscripción."""
    pass

# Acceso y permisos
class CodigoAccesoInvalido(InscripcionError):
    def __init__(self, codigo: str):
        super().__init__(f"Código de acceso inválido o expirado: {codigo}")

class AccesoInscripcionDenegado(InscripcionError):
    def __init__(self, usuario_id: int, sede_id: int):
        super().__init__(f"Usuario {usuario_id} no autorizado para operar en sede {sede_id}")

# Formulario
class FormularioNoEncontrado(InscripcionError):
    def __init__(self, formulario_id: int):
        super().__init__(f"Formulario {formulario_id} no encontrado")

class FormularioEstadoInvalido(InscripcionError):
    def __init__(self, estado: str, operacion: str):
        super().__init__(f"No se puede '{operacion}' con estado '{estado}'")

class SedeNoCoincide(InscripcionError):
    def __init__(self, recurso: str, sede_esperada: int, sede_recurso: int):
        super().__init__(f"La sede del {recurso} ({sede_recurso}) no coincide con la esperada ({sede_esperada})")

# Documentos
class DocumentoNoEncontrado(InscripcionError):
    def __init__(self, documento_id: int):
        super().__init__(f"Documento {documento_id} no encontrado")

class DocumentoInvalido(InscripcionError):
    def __init__(self, mensaje: str):
        super().__init__(mensaje)

class DocumentoTamanoExcedido(InscripcionError):
    def __init__(self, tamano: int, maximo: int):
        super().__init__(f"El archivo pesa {tamano} bytes y excede el límite {maximo} bytes")

class DocumentoMimeNoPermitido(InscripcionError):
    def __init__(self, mime: str):
        super().__init__(f"Tipo de archivo no permitido: {mime}")

class DocumentoProcesamientoInvalido(InscripcionError):
    def __init__(self, estado: str):
        super().__init__(f"Estado de procesamiento inválido para operación: {estado}")

class ArchivoDuplicadoHash(InscripcionError):
    def __init__(self, hash_archivo: str):
        super().__init__(f"Archivo duplicado (hash): {hash_archivo}")

# Firmas
class TipoFirmanteInvalido(InscripcionError):
    def __init__(self, tipo: str):
        super().__init__(f"Tipo de firmante inválido: {tipo}")

class FirmaDuplicada(InscripcionError):
    def __init__(self, formulario_id: int, tipo: str):
        super().__init__(f"Ya existe una firma de tipo '{tipo}' para el formulario {formulario_id}")

# Contratos
class ContratoNoEncontrado(InscripcionError):
    def __init__(self, contrato_id: int):
        super().__init__(f"Contrato {contrato_id} no encontrado")

class ContratoYaNumerado(InscripcionError):
    def __init__(self, contrato_id: int):
        super().__init__(f"Contrato {contrato_id} ya tiene numeración por sede")

class NumeracionNoDisponible(InscripcionError):
    def __init__(self, sede_id: int):
        super().__init__(f"No se pudo reservar numeración para sede {sede_id}")

# Turnos y precios
class TurnoNoDisponible(InscripcionError):
    def __init__(self, turno_id: int, sede_id: int):
        super().__init__(f"Turno {turno_id} no disponible para la sede {sede_id}")

