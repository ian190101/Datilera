# app/kernel/domain/acceso/ports.py
from __future__ import annotations

from typing import Protocol, Optional, Sequence, AsyncContextManager, runtime_checkable
from datetime import date, datetime

from .codigo_acceso_entidad import CodigoAcceso
from .codigo_acceso_uso_entidad import CodigoAccesoUso
from .estado_codigo_entidad import EstadoCodigo  # Enum/VO de estados (p.ej.: VIGENTE, EXPIRADO, REVOCADO, AGOTADO)


@runtime_checkable
class CodigoAccesoRepo(Protocol):
    """
    Puerto de acceso a Códigos de Acceso.

    Convenciones y reglas del dominio:
    - Longitud y formato del código: 6 caracteres alfanuméricos (validado en la capa de dominio/adaptador).
    - `guardar` aplica semántica de upsert (inserta/actualiza). No hace commit.
    - Los adaptadores deben traducir errores de infraestructura a errores de dominio (ver errors.py).
    - Vigencia: se consideran `fecha_inicio`/`fecha_fin` (y/o `activo`) en la entidad.
    - Uso/consumo: el consumo se registra en `CodigoAccesoUsoRepo` y el contador/estado se
      actualiza aquí dentro de la MISMA transacción (vía UnitOfWork).

    Estados usuales (sugeridos en EstadoCodigo):
    - VIGENTE, EXPIRADO, REVOCADO, AGOTADO, PENDIENTE (si aplica el flujo).
    """

    # --- Lectura/consulta ---
    async def obtener(self, codigo_id: int) -> Optional[CodigoAcceso]:
        """Retorna el código por id o None si no existe."""
        ...

    async def obtener_por_valor(self, valor: str) -> Optional[CodigoAcceso]:
        """Retorna el código por su valor (string de 6 chars) o None si no existe."""
        ...

    async def existe_valor(self, valor: str) -> bool:
        """True si ya existe un código con ese valor (para asegurar unicidad)."""
        ...

    async def listar_por_sede(
        self,
        sede_id: int,
        *,
        estados: Optional[Sequence[EstadoCodigo]] = None,
        rol_destino: Optional[str] = None,  # p.ej. "TUTOR", "PROFESORA"
        vigentes_en: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[CodigoAcceso]:
        """Lista códigos por sede con filtros opcionales y paginación."""
        ...

    async def listar_por_nino(
        self,
        nino_id: int,
        *,
        estados: Optional[Sequence[EstadoCodigo]] = None,
        vigentes_en: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[CodigoAcceso]:
        """Lista códigos asociados a un niño (tutores), con filtros y paginación."""
        ...

    async def listar(
        self,
        *,
        estados: Optional[Sequence[EstadoCodigo]] = None,
        rol_destino: Optional[str] = None,
        creado_en: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[CodigoAcceso]:
        """Listado general con filtros básicos y paginación."""
        ...

    # --- Escritura/actualización ---
    async def guardar(self, codigo: CodigoAcceso) -> None:
        """
        Inserta o actualiza el código (upsert). No confirma cambios.
        Recomendación: validar unicidad de `valor` y reglas de vigencia a nivel de dominio.
        """
        ...

    async def set_estado(self, codigo_id: int, estado: EstadoCodigo) -> None:
        """Actualiza el estado del código (ej.: REVOCADO, AGOTADO, EXPIRADO)."""
        ...

    async def incrementar_usos(self, codigo_id: int) -> None:
        """
        Incrementa el contador de usos realizados del código.
        Úsalo al consumir exitosamente (en conjunto con registrar uso y ajustar estado si se agotó).
        """
        ...

    async def revocar(self, codigo_id: int, *, motivo: Optional[str] = None) -> None:
        """Revoca el código (cambia estado a REVOCADO). No confirma cambios."""
        ...

    async def reactivar(self, codigo_id: int) -> None:
        """Reactiva un código revocado/pausado si las reglas lo permiten."""
        ...


@runtime_checkable
class CodigoAccesoUsoRepo(Protocol):
    """
    Puerto para registrar y consultar los usos (auditoría) de códigos de acceso.

    Notas:
    - Registrar tanto usos de tipo 'VERIFICACION' (check sin consumo, si deseas auditar),
      'CONSUMO' (creación de cuenta exitosa) y 'ENVIO_WHATSAPP' (auditar un intento de envío).
    - No hace commit; la UoW coordina la transacción.
    """

    async def registrar(self, uso: CodigoAccesoUso) -> None:
        """Persiste un uso/evento asociado a un código."""
        ...

    async def listar_por_codigo(
        self,
        codigo_id: int,
        *,
        tipo: Optional[str] = None,  # p.ej. 'CONSUMO', 'VERIFICACION', 'ENVIO_WHATSAPP'
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[CodigoAccesoUso]:
        """Lista eventos/uso por código con paginación."""
        ...

    async def contar_consumos_exitosos(self, codigo_id: int) -> int:
        """Retorna la cantidad de consumos exitosos (para comparar con usos_maximos)."""
        ...


@runtime_checkable
class UnitOfWork(Protocol, AsyncContextManager["UnitOfWork"]):
    """
    Unidad de Trabajo asíncrona (ACCESO) para coordinar transacciones.

    Política: COMMIT EXPLÍCITO (Patrón B)
    - `__aexit__`: hace rollback si hubo excepción; de lo contrario no hace commit automático.
    - Los servicios de aplicación deben invocar `await uow.commit()` en el camino feliz.
    """

    codigos: CodigoAccesoRepo
    codigos_usos: CodigoAccesoUsoRepo

    async def __aenter__(self) -> UnitOfWork: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    async def commit(self) -> None:
        """Confirma la transacción actual."""
        ...

    async def rollback(self) -> None:
        """Revierte la transacción actual."""
        ...