# app/infrastructure/db/repositories/calendario/tipos_eventos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime

from app.kernel.domain.calendario import (
    TipoEvento,
    TipoEventoRepositoryPort,
    TipoEventoNoEncontradoError,
    TipoEventoDuplicadoError,
    TipoEventoEnUsoError,
)
from app.infrastructure.db.models.calendario import TipoEvento as TipoEventoModel
from app.infrastructure.db.models.calendario import EventoCalendario as EventoCalendarioModel


class TiposEventosRepository(TipoEventoRepositoryPort):
    """Implementación del repositorio de tipos de eventos."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def crear(self, tipo: TipoEvento) -> TipoEvento:
        """Crea un nuevo tipo de evento.
        
        Args:
            tipo: Entidad TipoEvento a crear
            
        Returns:
            TipoEvento creado con ID asignado
            
        Raises:
            TipoEventoDuplicadoError: Si ya existe un tipo con ese nombre en la sede
        """
        # Verificar duplicados
        await self._verificar_duplicados(tipo.nombre, tipo.sede_id)
        
        # Crear modelo
        modelo = TipoEventoModel(
            **tipo.model_dump(exclude={"id", "actualizado_en"}, exclude_none=True)
        )
        
        self.session.add(modelo)
        await self.session.flush()
        await self.session.refresh(modelo)
        
        return TipoEvento.model_validate(modelo)
    
    async def obtener(self, tipo_id: int) -> Optional[TipoEvento]:
        """Obtiene un tipo de evento por ID.
        
        Args:
            tipo_id: ID del tipo de evento
            
        Returns:
            TipoEvento o None si no existe
        """
        stmt = select(TipoEventoModel).where(TipoEventoModel.id == tipo_id)
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        
        return TipoEvento.model_validate(modelo) if modelo else None
    
    async def listar(
        self,
        sede_id: Optional[int] = None,
        activo: Optional[bool] = None,
    ) -> List[TipoEvento]:
        """Lista tipos de eventos con filtros.
        
        Args:
            sede_id: Filtrar por sede (opcional)
            activo: Filtrar por estado activo/inactivo (opcional)
            
        Returns:
            Lista de TipoEvento
        """
        stmt = select(TipoEventoModel)
        
        # Aplicar filtros
        condiciones = []
        
        if sede_id is not None:
            condiciones.append(TipoEventoModel.sede_id == sede_id)
        
        if activo is not None:
            condiciones.append(TipoEventoModel.activo == activo)
        
        if condiciones:
            stmt = stmt.where(and_(*condiciones))
        
        # Ordenar alfabéticamente
        stmt = stmt.order_by(TipoEventoModel.nombre.asc())
        
        result = await self.session.execute(stmt)
        modelos = result.scalars().all()
        
        return [TipoEvento.model_validate(m) for m in modelos]
    
    async def actualizar(self, tipo: TipoEvento) -> TipoEvento:
        """Actualiza un tipo de evento existente.
        
        Args:
            tipo: Entidad TipoEvento con datos actualizados
            
        Returns:
            TipoEvento actualizado
            
        Raises:
            TipoEventoNoEncontradoError: Si el tipo no existe
            TipoEventoDuplicadoError: Si el nuevo nombre ya existe en la sede
        """
        # Obtener modelo existente
        stmt = select(TipoEventoModel).where(TipoEventoModel.id == tipo.id)
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        
        if not modelo:
            raise TipoEventoNoEncontradoError(tipo_id=tipo.id)
        
        # Verificar duplicados si cambió el nombre
        if modelo.nombre != tipo.nombre:
            await self._verificar_duplicados(tipo.nombre, tipo.sede_id, excluir_id=tipo.id)
        
        # Actualizar campos
        tipo.actualizado_en = datetime.utcnow()
        
        for campo, valor in tipo.model_dump(
            exclude={"id", "creado_en", "creado_por"},
            exclude_none=True
        ).items():
            setattr(modelo, campo, valor)
        
        await self.session.flush()
        await self.session.refresh(modelo)
        
        return TipoEvento.model_validate(modelo)
    
    async def activar_desactivar(self, tipo_id: int, activo: bool) -> TipoEvento:
        """Activa o desactiva un tipo de evento.
        
        Args:
            tipo_id: ID del tipo de evento
            activo: True para activar, False para desactivar
            
        Returns:
            TipoEvento actualizado
            
        Raises:
            TipoEventoNoEncontradoError: Si el tipo no existe
            TipoEventoEnUsoError: Si se intenta desactivar un tipo con eventos asociados
        """
        # Obtener modelo
        stmt = select(TipoEventoModel).where(TipoEventoModel.id == tipo_id)
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        
        if not modelo:
            raise TipoEventoNoEncontradoError(tipo_id=tipo_id)
        
        # Si se va a desactivar, verificar que no tenga eventos asociados
        if not activo:
            cantidad_eventos = await self._contar_eventos_asociados(tipo_id)
            if cantidad_eventos > 0:
                raise TipoEventoEnUsoError(tipo_id=tipo_id, cantidad_eventos=cantidad_eventos)
        
        # Actualizar estado
        modelo.activo = activo
        modelo.actualizado_en = datetime.utcnow()
        
        await self.session.flush()
        await self.session.refresh(modelo)
        
        return TipoEvento.model_validate(modelo)
    
    # =========================================================================
    # Métodos privados de ayuda
    # =========================================================================
    
    async def _verificar_duplicados(
        self, 
        nombre: str, 
        sede_id: int, 
        excluir_id: Optional[int] = None
    ) -> None:
        """Verifica si existe un tipo con el mismo nombre en la sede.
        
        Raises:
            TipoEventoDuplicadoError: Si ya existe
        """
        stmt = select(TipoEventoModel).where(
            and_(
                TipoEventoModel.nombre == nombre,
                TipoEventoModel.sede_id == sede_id
            )
        )
        
        if excluir_id:
            stmt = stmt.where(TipoEventoModel.id != excluir_id)
        
        result = await self.session.execute(stmt)
        existe = result.scalar_one_or_none()
        
        if existe:
            raise TipoEventoDuplicadoError(nombre=nombre, sede_id=sede_id)
    
    async def _contar_eventos_asociados(self, tipo_id: int) -> int:
        """Cuenta cuántos eventos están asociados al tipo.
        
        Args:
            tipo_id: ID del tipo de evento
            
        Returns:
            Cantidad de eventos asociados
        """
        stmt = select(func.count(EventoCalendarioModel.id)).where(
            EventoCalendarioModel.tipo_evento_id == tipo_id
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one()
