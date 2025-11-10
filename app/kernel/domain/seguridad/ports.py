# app/kernel/domain/seguridad/ports.py
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from .user_entidad import Usuario, Rol
from .permiso_entidad import Permiso

# ---------------------------------------------
# 1. Puertos de Salida: Repositorios (Persistence)
# ---------------------------------------------

class AbstractUserRepository(ABC):
    """Puerto para la persistencia de Usuarios."""
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[Usuario]:
        """Recupera un usuario por ID con sus roles y permisos cargados."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """Recupera un usuario por email (para login/autenticación)."""
        raise NotImplementedError
    
    @abstractmethod
    async def add(self, user: Usuario) -> Usuario:
        """Añade un nuevo usuario al sistema."""
        raise NotImplementedError
        
    @abstractmethod
    async def update(self, user: Usuario) -> Usuario:
        """Actualiza el estado de un usuario."""
        raise NotImplementedError

class AbstractRolRepository(ABC):
    """Puerto para la persistencia de Roles."""
    
    @abstractmethod
    async def get_by_nombre(self, nombre: str) -> Optional[Rol]:
        """Obtiene un Rol por su nombre único."""
        raise NotImplementedError

    @abstractmethod
    async def get_default_rol(self) -> Rol:
        """Obtiene el rol por defecto para nuevos registros."""
        raise NotImplementedError

# ---------------------------------------------
# 2. Puertos de Salida: Autenticación (Driven/Infraestructura)
# ---------------------------------------------

class AbstractTokenService(ABC):
    """Puerto para el servicio de creación y validación de tokens (JWT)."""
    
    @abstractmethod
    def create_access_token(self, user_id: int, sede_id: int, permisos: List[Permiso]) -> str:
        """Genera un JWT Access Token."""
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, user_id: int, jti: str) -> str:
        """Genera un JWT Refresh Token."""
        raise NotImplementedError
    
    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Decodifica y valida un token JWT."""
        raise NotImplementedError

# ---------------------------------------------
# 3. Puerto de Salida: Encriptación (Driven/Infraestructura)
# ---------------------------------------------

class AbstractHasher(ABC):
    """Puerto para servicios de hash de contraseñas (ej: bcrypt)."""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Convierte una contraseña en texto plano a un hash seguro."""
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica una contraseña de texto plano contra el hash."""
        raise NotImplementedError