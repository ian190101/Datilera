# app/kernel/domain/seguridad/ports.py

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from datetime import datetime

from .user_entidad import Usuario, Rol
from .permiso_entidad import Permiso, Accion
from .sede_entidad import Sede
from .usuario_rol_entidad import UsuarioRol
from .rol_permiso_entidad import RolPermiso

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
    async def crear(self, user: Usuario) -> Usuario:
        """Añade un nuevo usuario al sistema."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: Usuario) -> Usuario:
        """Actualiza el estado de un usuario."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[Usuario]:
        """Recupera un usuario por username."""
        raise NotImplementedError

    @abstractmethod
    async def update_perfil(self, usuario_id: int, data: dict) -> None:
        """Actualiza campos de perfil del usuario."""
        raise NotImplementedError

    @abstractmethod
    async def cambiar_estado(self, usuario_id: int, activo: bool) -> None:
        """Activa o desactiva un usuario."""
        raise NotImplementedError

    @abstractmethod
    async def list_paginated(
        self,
        page: int,
        per_page: int,
        sede_id: Optional[int] = None,
        rol_nombre: Optional[str] = None,
        activo: Optional[bool] = None,
        q: Optional[str] = None,
    ) -> Tuple[List[Usuario], int]:
        """
        Lista usuarios paginados con filtros.
        Retorna (items, total).
        """
        raise NotImplementedError

    @abstractmethod
    async def get_permisos_efectivos(self, usuario_id: int) -> List[Permiso]:
        """Obtiene todos los permisos efectivos de un usuario (a través de sus roles)."""
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


# ---------------------------------------------
# 4. Puerto de Salida: Sedes (Persistence)
# ---------------------------------------------
class AbstractSedeRepository(ABC):
    """Puerto para la persistencia de Sedes."""

    @abstractmethod
    async def get(self, sede_id: int) -> Optional[Sede]:
        """Obtiene una sede por ID."""
        raise NotImplementedError

    @abstractmethod
    async def exists(self, sede_id: int) -> bool:
        """True si la sede existe."""
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> List[Sede]:
        """Lista sedes."""
        raise NotImplementedError

    @abstractmethod
    async def crear(self, sede: Sede) -> Sede:
        """Añade una nueva sede al sistema."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_codigo(self, codigo: str) -> Optional[Sede]:
        """Obtiene una sede por código."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, sede_id: int, data: dict) -> Sede:
        """Actualiza campos de una sede y devuelve la entidad resultante."""
        raise NotImplementedError

    @abstractmethod
    async def delete_soft(self, sede_id: int) -> bool:
        """Desactiva (soft delete) una sede por ID, retorna True si aplicó."""
        raise NotImplementedError

    @abstractmethod
    async def list_paginated(
        self, page: int, per_page: int, activo: Optional[bool] = None
    ) -> Tuple[List[Sede], int]:
        """Lista sedes paginadas con filtro opcional por activo y retorna (items, total)."""
        raise NotImplementedError

# ---------------------------------------------
# 4. Puerto de Salida: Roles (Persistence)
# ---------------------------------------------
class AbstractRolRepository(ABC):
    """Puerto para la persistencia y consulta de Roles."""

    @abstractmethod
    async def get(self, rol_id: int) -> Optional[Rol]:
        """Obtiene un rol por ID con sus permisos."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_nombre(self, nombre: str) -> Optional[Rol]:
        """Obtiene un rol por su nombre único."""
        raise NotImplementedError

    @abstractmethod
    async def exists(self, rol_id: int) -> bool:
        """True si el rol existe."""
        raise NotImplementedError

    @abstractmethod
    async def list_paginated(
        self,
        page: int,
        per_page: int,
        activo: Optional[bool] = None,
        q: Optional[str] = None,
    ) -> Tuple[List[Rol], int]:
        """
        Lista roles paginados con filtro por activo y búsqueda opcional por nombre.
        Retorna (items, total).
        """
        raise NotImplementedError

    @abstractmethod
    async def crear(self, *, nombre: str, descripcion: Optional[str], activo: bool = True) -> Rol:
        """Crea un rol y retorna la entidad resultante."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, rol_id: int, data: dict) -> Rol:
        """Actualiza campos de un rol y retorna la entidad resultante."""
        raise NotImplementedError

    @abstractmethod
    async def delete_soft(self, rol_id: int) -> bool:
        """Desactiva (soft delete) un rol por ID, retorna True si aplicó."""
        raise NotImplementedError

    @abstractmethod
    async def get_default_rol(self) -> Rol:
        """Obtiene el rol por defecto para nuevos registros."""
        raise NotImplementedError
    
class AbstractUsuarioRolRepository(ABC):
    """Puerto para la gestión de asignaciones usuario-rol."""

    @abstractmethod
    async def ya_asignado(self, usuario_id: int, rol_id: int) -> bool:
        """True si el usuario ya tiene asignado el rol."""
        raise NotImplementedError

    @abstractmethod
    async def asignar(self, usuario_id: int, rol_id: int) -> None:
        """Asigna un rol a un usuario."""
        raise NotImplementedError

    @abstractmethod
    async def revocar(self, usuario_id: int, rol_id: int) -> bool:
        """Revoca un rol de un usuario. Retorna True si se revocó."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_usuario_y_rol(self, usuario_id: int, rol_id: int) -> Optional[UsuarioRol]:
        """Obtiene la asignación usuario-rol si existe."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_usuario(self, usuario_id: int) -> List[UsuarioRol]:
        """Lista todas las asignaciones de roles de un usuario."""
        raise NotImplementedError

class AbstractRolPermisoRepository(ABC):
    """Puerto para la gestión de asignaciones rol-permiso."""

    @abstractmethod
    async def ya_asignado(self, rol_id: int, permiso_id: int) -> bool:
        """True si el rol ya tiene asignado el permiso."""
        raise NotImplementedError

    @abstractmethod
    async def asignar(self, rol_id: int, permiso_id: int) -> None:
        """Asigna un permiso a un rol."""
        raise NotImplementedError

    @abstractmethod
    async def revocar(self, rol_id: int, permiso_id: int) -> bool:
        """Revoca un permiso de un rol. Retorna True si se revocó."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_rol_y_permiso(self, rol_id: int, permiso_id: int) -> Optional[RolPermiso]:
        """Obtiene la asignación rol-permiso si existe."""
        raise NotImplementedError

    @abstractmethod
    async def listar_por_rol(self, rol_id: int) -> List[RolPermiso]:
        """Lista todas las asignaciones de permisos de un rol."""
        raise NotImplementedError
    
class AbstractPermisoRepository(ABC):
    """Puerto para la persistencia de Permisos."""

    @abstractmethod
    async def get(self, permiso_id: int) -> Optional[Permiso]:
        """Obtiene un permiso por ID."""
        raise NotImplementedError

    @abstractmethod
    async def exists(self, permiso_id: int) -> bool:
        """True si el permiso existe."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_recurso_y_accion(self, recurso: str, accion: Accion) -> Optional[Permiso]:
        """Obtiene un permiso por recurso y acción (combinación única)."""
        raise NotImplementedError

    @abstractmethod
    async def list_paginated(
        self,
        page: int,
        per_page: int,
        activo: Optional[bool] = None,
        q: Optional[str] = None,
    ) -> Tuple[List[Permiso], int]:
        """
        Lista permisos paginados con filtro por activo y búsqueda opcional.
        Retorna (items, total).
        """
        raise NotImplementedError

    @abstractmethod
    async def crear(
        self, *, recurso: str, accion: Accion, descripcion: Optional[str], activo: bool = True
    ) -> Permiso:
        """Crea un permiso y retorna la entidad resultante."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, permiso_id: int, data: dict) -> Permiso:
        """Actualiza campos de un permiso y retorna la entidad resultante."""
        raise NotImplementedError

    @abstractmethod
    async def delete_soft(self, permiso_id: int) -> bool:
        """Desactiva (soft delete) un permiso por ID, retorna True si aplicó."""
        raise NotImplementedError