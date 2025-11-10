# app/kernel/domain/academico/ports.py
from __future__ import annotations

from typing import Protocol, Optional, Sequence, AsyncContextManager, runtime_checkable
from datetime import date

from .grupos_entidad import Grupo
from .paralelos_entidad import Paralelo
from .horarios_entidad import Horario
from .horarios_paralelos_entidad import HorarioParalelo
from .paralelos_profesoras_entidad import ParaleloProfesora


@runtime_checkable
class GrupoRepo(Protocol):
    """
    Puerto de acceso a Grupos del subdominio académico.

    Convenciones:
    - `guardar` aplica semántica de upsert (inserta o actualiza según corresponda).
    - Los cambios NO se confirman aquí; el `UnitOfWork` se encarga de `commit/rollback`.
    - Los adaptadores deben levantar errores de dominio (ver errors.py) y NO
      propagar errores de la DB.
    """

    async def obtener(self, grupo_id: int) -> Optional[Grupo]:
        """Retorna el grupo por id o None si no existe."""
        ...

    async def guardar(self, grupo: Grupo) -> None:
        """Inserta o actualiza el grupo. No hace commit."""
        ...

    async def listar_por_sede(
        self,
        sede_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Grupo]:
        """Lista grupos de una sede con paginación (limit/offset)."""
        ...

    async def next_id(self) -> int:
        """
        (Opcional) Devuelve el próximo id disponible, si el adaptador lo soporta.
        Si usas autoincrement/UUID desde la DB, puedes:
        - implementar un stub que levante NotImplementedError, o
        - no usar este método en absoluto.
        """
        ...


@runtime_checkable
class ParaleloRepo(Protocol):
    """
    Puerto de acceso a Paralelos.

    Convenciones:
    - `guardar` es upsert y no confirma cambios.
    - Levantar errores de dominio ante invariantes violadas (no errores de DB).
    """

    async def obtener(self, paralelo_id: int) -> Optional[Paralelo]:
        """Retorna el paralelo por id o None si no existe."""
        ...

    async def guardar(self, paralelo: Paralelo) -> None:
        """Inserta o actualiza el paralelo. No hace commit."""
        ...

    async def listar_por_grupo(
        self,
        grupo_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Paralelo]:
        """Lista paralelos de un grupo con paginación (limit/offset)."""
        ...

    async def next_id(self) -> int:
        """
        (Opcional) Próximo id disponible si el adaptador lo soporta.
        En sistemas con autoincrement/UUID, ver nota en GrupoRepo.next_id.
        """
        ...


@runtime_checkable
class HorarioRepo(Protocol):
    """
    Puerto de acceso a Horarios.
    """

    async def obtener(self, horario_id: int) -> Optional[Horario]:
        """Retorna el horario por id o None si no existe."""
        ...

    async def guardar(self, horario: Horario) -> None:
        """Inserta o actualiza el horario. No hace commit."""
        ...

    async def listar_por_paralelo(
        self,
        paralelo_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Horario]:
        """Lista horarios asociados a un paralelo, con paginación."""
        ...

    async def next_id(self) -> int:
        """
        (Opcional) Próximo id disponible si el adaptador lo soporta.
        En sistemas con autoincrement/UUID, ver nota en GrupoRepo.next_id.
        """
        ...


@runtime_checkable
class HorarioParaleloRepo(Protocol):
    """
    Puerto para enlaces Horario-Paralelo (vigencias de horarios por paralelo).
    """

    async def obtener(self, enlace_id: int) -> Optional[HorarioParalelo]:
        """Retorna el enlace por id o None si no existe."""
        ...

    async def guardar(self, enlace: HorarioParalelo) -> None:
        """Inserta o actualiza el enlace Horario-Paralelo. No hace commit."""
        ...

    async def listar_por_paralelo(
        self,
        paralelo_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
        vigentes_en: Optional[date] = None,
    ) -> Sequence[HorarioParalelo]:
        """
        Lista enlaces por paralelo con paginación.
        - Si `vigentes_en` se provee, filtra por aquellos vigentes en esa fecha.
        """
        ...

    async def listar_por_horario(
        self,
        horario_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[HorarioParalelo]:
        """Lista enlaces por horario (histórico completo) con paginación."""
        ...


@runtime_checkable
class ParaleloProfesoraRepo(Protocol):
    """
    Puerto para asignaciones de Profesoras a Paralelos.
    """

    async def obtener(self, asignacion_id: int) -> Optional[ParaleloProfesora]:
        """Retorna la asignación por id o None si no existe."""
        ...

    async def guardar(self, asignacion: ParaleloProfesora) -> None:
        """Inserta o actualiza la asignación. No hace commit."""
        ...

    async def vigentes_por_paralelo(
        self,
        paralelo_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[ParaleloProfesora]:
        """Lista asignaciones vigentes para un paralelo, con paginación."""
        ...

    async def historico_por_paralelo(
        self,
        paralelo_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[ParaleloProfesora]:
        """Lista el histórico completo de asignaciones para un paralelo, con paginación."""
        ...


@runtime_checkable
class UnitOfWork(Protocol, AsyncContextManager["UnitOfWork"]):
    """
    Unidad de Trabajo asíncrona para coordinar transacciones.

    Política recomendada (Patrón B - COMMIT EXPLÍCITO):
    - `__aexit__` debe hacer `rollback()` si hubo excepción.
    - Si no hubo excepción, NO debe hacer commit automático.
    - El servicio de aplicación debe invocar `await uow.commit()` en el caso feliz.
    """

    # Repositorios expuestos como atributos (no propiedades) para mayor flexibilidad.
    grupos: GrupoRepo
    paralelos: ParaleloRepo
    horarios: HorarioRepo
    horarios_paralelos: HorarioParaleloRepo
    paralelos_profesoras: ParaleloProfesoraRepo

    async def __aenter__(self) -> UnitOfWork: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    async def commit(self) -> None:
        """Confirma la transacción actual."""
        ...

    async def rollback(self) -> None:
        """Revierte la transacción actual."""
        ...