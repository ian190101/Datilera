# app/kernel/application/seguridad/refresh_token.py
from pydantic import BaseModel
from app.kernel.domain.common.excepciones import InvalidCredentialsError, UserInactiveError
from app.kernel.domain.seguridad.ports import AbstractUserRepository, AbstractTokenService
from .login import Login # Reutilizamos DTO de respuesta
from typing import List
from .asignar_permiso_rol import Permiso 

# DTOs
class RefrescarTokenRequest(BaseModel):
    refresh_token: str

# Caso de Uso
class RefrescarToken:
    def __init__(self, user_repo: AbstractUserRepository, token_service: AbstractTokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    async def execute(self, request: RefrescarTokenRequest) -> Login:
        
        # 1. Decodificar y Validar Refresh Token
        try:
            payload = self.token_service.decode_token(request.refresh_token)
            user_id = payload.get("sub")
            jti = payload.get("jti")
            token_type = payload.get("type")
        except Exception:
            # Token inválido (expirado, firma mala, etc.)
            raise InvalidCredentialsError("Token de refresco inválido o expirado.")
        
        if not (user_id and token_type == "refresh"):
             raise InvalidCredentialsError("Token de refresco no válido.")
        
        # Opcional: Verificar JTI en lista de revocados (DB) aquí.
        
        # 2. Obtener Usuario
        user = await self.user_repo.get_by_id(int(user_id))
        
        if not user:
            raise InvalidCredentialsError("Usuario asociado al token no encontrado.")
            
        if not user.activo:
            raise UserInactiveError()
            
        # 3. Generar Nuevo Par de Tokens
        permisos_dominio: List[Permiso] = []
        for rol in user.roles:
            permisos_dominio.extend(rol.permisos)
        
        permisos_set = {p.nombre_completo for p in permisos_dominio}

        # Se reutiliza el mismo JTI para el nuevo refresh token (Rotate-on-Use)
        access_token = self.token_service.create_access_token(
            user_id=user.id, 
            sede_id=user.sede_id, 
            permisos=list(permisos_set)
        )
        new_refresh_token = self.token_service.create_refresh_token(
            user_id=user.id,
            jti=jti
        )

        return Login(
            access_token=access_token,
            refresh_token=new_refresh_token, # Importante devolver el nuevo refresh token
            usuario_id=user.id,
            nombre_completo=user.nombre_completo,
            permisos=list(permisos_set)
        )