# app/interfaces/api/v1/deps.py
from __future__ import annotations

from functools import lru_cache
from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.db.uow import UnitOfWork

# Servicios técnicos (adapters)
from app.infrastructure.auth.auth_utils import PasslibHasher, PyJWTTokenService

# Repositorios de infraestructura
from app.infrastructure.db.repositories.seguridad.usuarios_repo import UsuariosRepository
from app.infrastructure.db.repositories.seguridad.roles_repo import RolesRepository
from app.infrastructure.db.repositories.seguridad.usuarios_roles import UsuarioRolRepository
from app.infrastructure.db.repositories.seguridad.sesiones_repo import SesionesRepository
from app.infrastructure.db.repositories.seguridad.tokens_revocados_repo import TokensRevocadosRepository
from app.infrastructure.db.repositories.auditoria.auditoria_acciones_repo import AuditoriaAccionesRepository
from app.infrastructure.messaging.whatsapp_stub import WhatsappStubService

@lru_cache
def _cached_settings() -> Settings:
    return get_settings()

def get_settings_dep() -> Settings:
    return _cached_settings()

async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_uow_dep(session: AsyncSession = Depends(get_session)) -> AsyncIterator[UnitOfWork]:
    async with UnitOfWork(session) as uow:
        yield uow

# Adapters para puertos del dominio
def get_hasher() -> PasslibHasher:
    return PasslibHasher()

def get_tokens(settings: Settings = Depends(get_settings_dep)) -> PyJWTTokenService:
    return PyJWTTokenService(settings)

# Repositorios
def get_usuarios_repo(session: AsyncSession = Depends(get_session)) -> UsuariosRepository:
    return UsuariosRepository(session)

def get_roles_repo(session: AsyncSession = Depends(get_session)) -> RolesRepository:
    return RolesRepository(session)

def get_usuarios_roles_repo(session: AsyncSession = Depends(get_session)) -> UsuarioRolRepository:
    return UsuarioRolRepository(session)

def get_sesiones_repo(session: AsyncSession = Depends(get_session)) -> SesionesRepository:
    return SesionesRepository(session)

def get_revocados_repo(session: AsyncSession = Depends(get_session)) -> TokensRevocadosRepository:
    return TokensRevocadosRepository(session)

def get_auditoria_repo(session: AsyncSession = Depends(get_session)) -> AuditoriaAccionesRepository:
    return AuditoriaAccionesRepository(session)

def get_whatsapp_sender() -> WhatsappStubService:
    return WhatsappStubService()