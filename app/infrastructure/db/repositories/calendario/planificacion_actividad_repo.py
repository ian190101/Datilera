# app/infrastructure/db/repositories/calendario/planificacion_actividad_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional
from datetime import date, time, datetime

from app.kernel.domain.calendario import (
    PlanificacionActividad,
    PlanificacionActividadRepositoryPort,
    PlanificacionNoEncontradaError,
    PlanificacionHorarioConflictoError,
)
from app.infrastructure.db.models.calendario import PlanificacionActividad as PlanificacionActividadModel


class PlanificacionActividadRepository(PlanificacionActividadRepositoryPort):
    """Implementación del repositorio de planificaciones de actividades."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def crear(self, planificacion: PlanificacionActividad) -> PlanificacionActividad:
        """Crea una nueva planificación.
        
        Args:
            planificacion: Entidad PlanificacionActividad a crear
            
        Returns:
            PlanificacionActividad creada con ID asignado
            
        Raises:
            PlanificacionHorarioConflictoError: Si hay conflicto de horarios
        """
        # Verificar conflictos de horario
        await self._verificar_conflicto_horario(planificacion)
        
        modelo = PlanificacionActividadModel(
            **planificacion.model_dump(exclude={"id", "actualizado_en"}, exclude_none=True)
        )
        
        self.session.add(modelo)
        await self.session.flush()
        await self.session.refresh(modelo)
        
        return PlanificacionActividad.model_validate(modelo)
    
    async def obtener(self, planificacion_id: int) -> Optional[PlanificacionActividad]:
        """Obtiene una planificación por ID.
        
        Args:
            planificacion_id: ID de la planificación
            
        Returns:
            PlanificacionActividad o None si no existe
        """
        stmt = select(PlanificacionActividadModel).where(
            PlanificacionActividadModel.id == planificacion_id
        )
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        
        return PlanificacionActividad.model_validate(modelo) if modelo else None
    
    async def listar_por_fecha(
        self,
        fecha: date,
        sede_id: Optional[int] = None,
        profesora_id: Optional[int] = None,
        paralelo_id: Optional[int] = None,
    ) -> List[PlanificacionActividad]:
        """Lista planificaciones de una fecha específica.
        
        Args:
            fecha: Fecha a consultar
            sede_id: Filtrar por sede (opcional)
            profesora_id: Filtrar por profesora (opcional)
            paralelo_id: Filtrar por paralelo (opcional)
            
        Returns:
            Lista de PlanificacionActividad ordenada por hora
        """
        stmt = select(PlanificacionActividadModel).where(
            PlanificacionActividadModel.fecha == fecha
        )
        
        # Aplicar filtros opcionales
        if sede_id is not None:
            stmt = stmt.where(PlanificacionActividadModel.sede_id == sede_id)
        
        if profesora_id is not None:
            stmt = stmt.where(PlanificacionActividadModel.profesora_id == profesora_id)
        
        if paralelo_id is not None:
            stmt = stmt.where(PlanificacionActividadModel.paralelo_id == paralelo_id)
        
        # Ordenar por hora de inicio
        stmt = stmt.order_by(PlanificacionActividadModel.hora_inicio.asc())
        
        result = await self.session.execute(stmt)
        modelos = result.scalars().all()
        
        return [PlanificacionActividad.model_validate(m) for m in modelos]
    
    async def listar_por_rango(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        sede_id: Optional[int] = None,
        profesora_id: Optional[int] = None,
    ) -> List[PlanificacionActividad]:
        """Lista planificaciones en un rango de fechas.
        
        Args:
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            sede_id: Filtrar por sede (opcional)
            profesora_id: Filtrar por profesora (opcional)
            
        Returns:
            Lista de PlanificacionActividad ordenada por fecha y hora
        """
        stmt = select(PlanificacionActividadModel).where(
            and_(
                PlanificacionActividadModel.fecha >= fecha_inicio,
                PlanificacionActividadModel.fecha <= fecha_fin
            )
        )
        
        # Aplicar filtros opcionales
        if sede_id is not None:
            stmt = stmt.where(PlanificacionActividadModel.sede_id == sede_id)
        
        if profesora_id is not None:
            stmt = stmt.where(PlanificacionActividadModel.profesora_id == profesora_id)
        
        # Ordenar por fecha y hora
        stmt = stmt.order_by(
            PlanificacionActividadModel.fecha.asc(),
            PlanificacionActividadModel.hora_inicio.asc()
        )
        
        result = await self.session.execute(stmt)
        modelos = result.scalars().all()
        
        return [PlanificacionActividad.model_validate(m) for m in modelos]
    
    async def actualizar(self, planificacion: PlanificacionActividad) -> PlanificacionActividad:
        """Actualiza una planificación existente.
        
        Args:
            planificacion: Entidad PlanificacionActividad con datos actualizados
            
        Returns:
            PlanificacionActividad actualizada
            
        Raises:
            PlanificacionNoEncontradaError: Si la planificación no existe
            PlanificacionHorarioConflictoError: Si el nuevo horario genera conflicto
        """
        # Obtener modelo existente
        stmt = select(PlanificacionActividadModel).where(
            PlanificacionActividadModel.id == planificacion.id
        )
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        
        if not modelo:
            raise PlanificacionNoEncontradaError(planificacion_id=planificacion.id)
        
        # Verificar conflictos de horario si cambió fecha u horarios
        if (modelo.fecha != planificacion.fecha or 
            modelo.hora_inicio != planificacion.hora_inicio or
            modelo.hora_fin != planificacion.hora_fin or
            modelo.profesora_id != planificacion.profesora_id):
            await self._verificar_conflicto_horario(planificacion, excluir_id=planificacion.id)
        
        # Actualizar timestamp
        planificacion.actualizado_en = datetime.utcnow()
        
        # Actualizar campos
        for campo, valor in planificacion.model_dump(
            exclude={"id", "creado_en"},
            exclude_none=True
        ).items():
            setattr(modelo, campo, valor)
        
        await self.session.flush()
        await self.session.refresh(modelo)
        
        return PlanificacionActividad.model_validate(modelo)
    
    async def eliminar(self, planificacion_id: int) -> bool:
        """Elimina una planificación.
        
        Args:
            planificacion_id: ID de la planificación a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        stmt = select(PlanificacionActividadModel).where(
            PlanificacionActividadModel.id == planificacion_id
        )
        result = await self.session.execute(stmt)
        modelo = result.scalar_one_or_none()
        
        if not modelo:
            return False
        
        await self.session.delete(modelo)
        await self.session.flush()
        
        return True
    
    # =========================================================================
    # Métodos privados de ayuda
    # =========================================================================
    
    async def _verificar_conflicto_horario(
        self, 
        planificacion: PlanificacionActividad,
        excluir_id: Optional[int] = None
    ) -> None:
        """Verifica si hay conflicto de horarios con otras planificaciones.
        
        Un conflicto ocurre cuando:
        - Misma profesora
        - Misma fecha
        - Horarios se solapan
        
        Raises:
            PlanificacionHorarioConflictoError: Si hay conflicto
        """
        # Buscar planificaciones de la misma profesora en la misma fecha
        stmt = select(PlanificacionActividadModel).where(
            and_(
                PlanificacionActividadModel.profesora_id == planificacion.profesora_id,
                PlanificacionActividadModel.fecha == planificacion.fecha
            )
        )
        
        if excluir_id:
            stmt = stmt.where(PlanificacionActividadModel.id != excluir_id)
        
        result = await self.session.execute(stmt)
        planificaciones_existentes = result.scalars().all()
        
        # Verificar solapamiento de horarios
        for existente in planificaciones_existentes:
            if self._horarios_se_solapan(
                planificacion.hora_inicio, planificacion.hora_fin,
                existente.hora_inicio, existente.hora_fin
            ):
                raise PlanificacionHorarioConflictoError(
                    fecha=str(planificacion.fecha),
                    hora_inicio=str(planificacion.hora_inicio),
                    hora_fin=str(planificacion.hora_fin)
                )
    
    @staticmethod
    def _horarios_se_solapan(
        inicio1: time, fin1: time,
        inicio2: time, fin2: time
    ) -> bool:
        """Determina si dos rangos horarios se solapan.
        
        Args:
            inicio1, fin1: Rango horario 1
            inicio2, fin2: Rango horario 2
            
        Returns:
            True si se solapan, False si no
        """
        # Los horarios se solapan si:
        # inicio1 está entre inicio2 y fin2, O
        # fin1 está entre inicio2 y fin2, O
        # inicio2 está entre inicio1 y fin1
        return (
            (inicio2 <= inicio1 < fin2) or
            (inicio2 < fin1 <= fin2) or
            (inicio1 <= inicio2 < fin1)
        )
    
    async def obtener_planificaciones_pendientes(
        self,
        fecha_limite: date,
        sede_id: Optional[int] = None
    ) -> List[PlanificacionActividad]:
        """Obtiene planificaciones no completadas hasta una fecha.
        
        Args:
            fecha_limite: Fecha límite
            sede_id: Filtrar por sede (opcional)
            
        Returns:
            Lista de planificaciones pendientes
        """
        stmt = select(PlanificacionActividadModel).where(
            and_(
                PlanificacionActividadModel.fecha <= fecha_limite,
                PlanificacionActividadModel.completada == False
            )
        )
        
        if sede_id is not None:
            stmt = stmt.where(PlanificacionActividadModel.sede_id == sede_id)
        
        stmt = stmt.order_by(PlanificacionActividadModel.fecha.asc())
        
        result = await self.session.execute(stmt)
        modelos = result.scalars().all()
        
        return [PlanificacionActividad.model_validate(m) for m in modelos]
