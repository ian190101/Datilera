# app/kernel/domain/common/excepciones.py
# Lo ubicamos en common ya que es transversal al dominio
class BaseDominioError(Exception):
    """Base para todos los errores de Dominio/Negocio."""
    status_code: int = 500
    code: str = "GENERIC_ERROR"
    message: str = "Ha ocurrido un error inesperado en el negocio."
    
    def __init__(self, message: str = None, details: dict = None, status_code: int = None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class InvalidCredentialsError(BaseDominioError):
    """Error al intentar autenticar con credenciales inválidas."""
    status_code = 401 # Unauthorized
    code = "INVALID_CREDENTIALS"
    message = "Correo electrónico o contraseña incorrectos."

class UserInactiveError(BaseDominioError):
    """Error cuando el usuario existe pero está inactivo."""
    status_code = 403 # Forbidden (Acceso denegado por estado)
    code = "USER_INACTIVE"
    message = "La cuenta está inactiva. Contacte a su administrador."

class RBACDenegadoError(BaseDominioError):
    """Error cuando un usuario no tiene los permisos necesarios."""
    status_code = 403 # Forbidden
    code = "RBAC_DENIED"
    message = "Acceso denegado. Permiso insuficiente."

class NotFoundError(BaseDominioError):
    """Error de entidad no encontrada."""
    status_code = 404
    code = "NOT_FOUND"
    message = "El recurso solicitado no fue encontrado."

# Se debe importar esto en app/main.py