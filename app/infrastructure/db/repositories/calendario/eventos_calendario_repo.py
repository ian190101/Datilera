# app/infrastructure/db/repositories/calendario/eventos_calendario_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional
from datetime import date, datetime

from app.kernel.domain.calendario import (
    EventoCalendario,
    EventoCalendarioRepositoryPort,
    EventoNoEncontradoError,
)
from app.infrastructure.db.models.calendario import EventoCalendario as EventoCalendarioModel


class EventosCalendarioRepository(EventoCalendarioRepositoryPort):
    """Implementación del repositorio de eventos del calendario."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def crear(self, evento: EventoCalendario) -> EventoCalendario:
        """Crea un nuevo evento.
        
        Args:
            evento: Entidad EventoCalendario a crear
            
        Returns:
            EventoCalendario creado con ID asignado
        """
        modelo = EventoCalendarioModel(
            **evento.model_dump(
                exclude={"id", "actualizado_en", "aprobado_por", "aprobado_en"},
                exclude_none=True
            )
        )
        
        self.session.add(modelo)
        await self.session.flush()
        await self.session.refresh(modelo)
        
        return EventoCalendario.model_validate(modelo)
    
    async def obtener(self, evento_id: int) -> Optional[EventoCalendario]:
        """Obtiene un evento por ID.
        
        Args:
            evento_id: ID del evento
            
        Returns:
            EventoCalendario o None si no existe
        """
        stmt = select(EventoCalendarioModel).where(EventoCalendarioModel.id == evento_id)
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        
        return EventoCalendario.model_validate(modelo) if modelo else None
    
    async def listar(
        self,
        sede_id: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        tipo_evento_id: Optional[int] = None,
        aprobado: Optional[bool] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> List[EventoCalendario]:
        """Lista eventos con filtros.
        
        Args:
            sede_id: Filtrar por sede
            fecha_inicio: Fecha inicio del rango
            fecha_fin: Fecha fin del rango
            tipo_evento_id: Filtrar por tipo de evento
            aprobado: Filtrar por estado de aprobación
            limite: Máximo de resultados
            offset: Saltar registros
            
        Returns:
            Lista de EventoCalendario
        """
        stmt = select(EventoCalendarioModel)
        
        # Aplicar filtros
        condiciones = []
        
        if sede_id is not None:
            condiciones.append(EventoCalendarioModel.sede_id == sede_id)
        
        if fecha_inicio is not None:
            # Incluir eventos que empiezan después de fecha_inicio
            # o que terminan después de fecha_inicio (eventos multi-día)
            condiciones.append(
                or_(
                    EventoCalendarioModel.fecha >= fecha_inicio,
                    and_(
                        EventoCalendarioModel.fecha_fin.isnot(None),
                        EventoCalendarioModel.fecha_fin >= fecha_inicio
                    )
                )
            )
        
        if fecha_fin is not None:
            # Incluir eventos que empiezan antes de fecha_fin
            condiciones.append(EventoCalendarioModel.fecha <= fecha_fin)
        
        if tipo_evento_id is not None:
            condiciones.append(EventoCalendarioModel.tipo_evento_id == tipo_evento_id)
        
        if aprobado is not None:
            condiciones.append(EventoCalendarioModel.aprobado == aprobado)
        
        if condiciones:
            stmt = stmt.where(and_(*condiciones))
        
        # Ordenar por fecha (más próximos primero)
        stmt = stmt.order_by(EventoCalendarioModel.fecha.asc())
        
        # Paginación
        stmt = stmt.limit(limite).offset(offset)
        
        result = await self.session.execute(stmt)
        modelos = result.scalars().all()
        
        return [EventoCalendario.model_validate(m) for m in modelos]
    
    async def actualizar(self, evento: EventoCalendario) -> EventoCalendario:
        """Actualiza un evento existente.
        
        Args:
            evento: Entidad EventoCalendario con datos actualizados
            
        Returns:
            EventoCalendario actualizado
            
        Raises:
            EventoNoEncontradoError: Si el evento no existe
        """
        # Obtener modelo existente
        stmt = select(EventoCalendarioModel).where(EventoCalendarioModel.id == evento.id)
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        
        if not modelo:
            raise EventoNoEncontradoError(evento_id=evento.id)
        
        # Actualizar timestamp
        evento.actualizado_en = datetime.utcnow()
        
        # Actualizar campos
        for campo, valor in evento.model_dump(
            exclude={"id", "creado_en", "creado_por"},
            exclude_none=True
        ).items():
            setattr(modelo, campo, valor)
        
        await self.session.flush()
        await self.session.refresh(modelo)
        
        return EventoCalendario.model_validate(modelo)
    
    async def eliminar(self, evento_id: int) -> bool:
        """Elimina un evento.
        
        Args:
            evento_id: ID del evento a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        stmt = select(EventoCalendarioModel).where(EventoCalendarioModel.id == evento_id)
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        
        if not modelo:
            return False
        
        await self.session.delete(modelo)
        await self.session.flush()
        
        return True
    
    # =========================================================================
    # Métodos adicionales útiles
    # =========================================================================
    
    async def obtener_eventos_pendientes_aprobacion(self, sede_id: int) -> List[EventoCalendario]:
        """Obtiene eventos pendientes de aprobación de una sede.
        
        Args:
            sede_id: ID de la sede
            
        Returns:
            Lista de eventos pendientes
        """
        stmt = select(EventoCalendarioModel).where(
            and_(
                EventoCalendarioModel.sede_id == sede_id,
                EventoCalendarioModel.aprobado == False
            )
        ).order_by(EventoCalendarioModel.fecha.asc())
        
        result = await self.session.execute(stmt)
        modelos = result.scalars().all()
        
        return [EventoCalendario.model_validate(m) for m in modelos]
    
    async def obtener_eventos_con_recordatorio_pendiente(
        self, 
        fecha_actual: date
    ) -> List[EventoCalendario]:
        """Obtiene eventos que necesitan enviar recordatorio.
        
        Args:
            fecha_actual: Fecha actual para calcular días restantes
            
        Returns:
            Lista de eventos con recordatorio pendiente
        """
        stmt = select(EventoCalendarioModel).where(
            and_(
                EventoCalendarioModel.recordatorio_dias_antes.isnot(None),
                EventoCalendarioModel.recordatorio_enviado == False,
                EventoCalendarioModel.aprobado == True,
                EventoCalendarioModel.fecha >= fecha_actual
            )
        )
        
        result = await self.session.execute(stmt)
        modelos = result.scalars().all()
        
        # Filtrar por días restantes (esto idealmente debería ser en la query)
        eventos_a_notificar = []
        for modelo in modelos:
            dias_restantes = (modelo.fecha - fecha_actual).days
            if dias_restantes <= modelo.recordatorio_dias_antes:
                eventos_a_notificar.append(EventoCalendario.model_validate(modelo))
        
        return eventos_a_notificar
