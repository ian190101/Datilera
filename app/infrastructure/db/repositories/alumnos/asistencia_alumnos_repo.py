# app/infrastructure/db/repositories/alumnos/asistencia_alumnos_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, and_
from typing import Dict, Any, Sequence, Optional
from datetime import date

from app.infrastructure.db.models.alumnos.asistencia_alumnos import AsistenciaAlumno


class AsistenciaAlumnosRepository:
    """Repositorio para gestión de asistencia de alumnos."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def crear(self, data: dict) -> AsistenciaAlumno:
        """Registrar asistencia de un alumno."""
        asistencia = AsistenciaAlumno(**data)
        self.session.add(asistencia)
        await self.session.commit()
        await self.session.refresh(asistencia)
        return asistencia
    
    async def obtener_por_id(self, id: int) -> Optional[AsistenciaAlumno]:
        """Obtener registro de asistencia por ID."""
        result = await self.session.execute(
            select(AsistenciaAlumno).where(AsistenciaAlumno.id == id)
        )
        return result.scalar_one_or_none()
    
    async def obtener_por_alumno_fecha(
        self, 
        alumno_id: int, 
        fecha: date
    ) -> Optional[AsistenciaAlumno]:
        """Obtener asistencia de un alumno en una fecha específica."""
        result = await self.session.execute(
            select(AsistenciaAlumno).where(
                and_(
                    AsistenciaAlumno.alumno_id == alumno_id,
                    AsistenciaAlumno.fecha == fecha
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def listar_por_alumno(
        self, 
        alumno_id: int, 
        fecha_desde: Optional[date] = None, 
        fecha_hasta: Optional[date] = None
    ) -> Sequence[AsistenciaAlumno]:
        """Listar asistencias de un alumno en un rango de fechas."""
        query = select(AsistenciaAlumno).where(AsistenciaAlumno.alumno_id == alumno_id)
        
        if fecha_desde:
            query = query.where(AsistenciaAlumno.fecha >= fecha_desde)
        if fecha_hasta:
            query = query.where(AsistenciaAlumno.fecha <= fecha_hasta)
        
        query = query.order_by(AsistenciaAlumno.fecha.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def listar_por_sede_fecha(
        self, 
        sede_id: int, 
        fecha: date
    ) -> Sequence[AsistenciaAlumno]:
        """Listar todas las asistencias de una sede en una fecha."""
        result = await self.session.execute(
            select(AsistenciaAlumno).where(
                and_(
                    AsistenciaAlumno.sede_id == sede_id,
                    AsistenciaAlumno.fecha == fecha
                )
            )
        )
        return result.scalars().all()
    
    async def actualizar(self, id: int, data: dict) -> Optional[AsistenciaAlumno]:
        """Actualizar registro de asistencia (ej: agregar hora_salida)."""
        asistencia = await self.obtener_por_id(id)
        if asistencia:
            for key, value in data.items():
                setattr(asistencia, key, value)
            await self.session.commit()
            await self.session.refresh(asistencia)
        return asistencia
    
    # =========================================================================
    # MÉTODOS PARA ESTADÍSTICAS
    # =========================================================================
    
    async def obtener_estadisticas_paralelo(
        self,
        paralelo_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de asistencia de un paralelo.
        
        Args:
            paralelo_id: ID del paralelo
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            
        Returns:
            Diccionario con estadísticas:
            - total_registros, total_presentes, total_tarde, etc.
            - porcentaje_asistencia, porcentaje_retrasos
        """
        query = select(
            func.count(AsistenciaAlumno.id).label('total_registros'),
            func.count(
                case((AsistenciaAlumno.estado == 'presente', 1))
            ).label('total_presentes'),
            func.count(
                case((AsistenciaAlumno.estado == 'tarde', 1))
            ).label('total_tarde'),
            func.count(
                case((AsistenciaAlumno.estado == 'ausente', 1))
            ).label('total_ausente'),
            func.count(
                case((AsistenciaAlumno.estado == 'justificado', 1))
            ).label('total_justificado'),
        ).where(
            and_(
                AsistenciaAlumno.paralelo_id == paralelo_id,
                AsistenciaAlumno.fecha >= fecha_inicio,
                AsistenciaAlumno.fecha <= fecha_fin
            )
        )
        
        result = await self.session.execute(query)
        row = result.first()
        
        # Validar que row no sea None
        if not row:
            return {
                'paralelo_id': paralelo_id,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'total_registros': 0,
                'total_presentes': 0,
                'total_tarde': 0,
                'total_ausente': 0,
                'total_justificado': 0,
                'porcentaje_asistencia': 0.0,
                'porcentaje_retrasos': 0.0,
            }
        
        # Acceder por índice (orden del select)
        total_registros: int = row[0] or 0
        total_presentes: int = row[1] or 0
        total_tarde: int = row[2] or 0
        total_ausente: int = row[3] or 0
        total_justificado: int = row[4] or 0
        
        # Calcular porcentajes
        total = total_registros or 1  # Evitar división por cero
        porcentaje_asistencia = round((total_presentes / total) * 100, 2) if total > 0 else 0.0
        porcentaje_retrasos = round((total_tarde / total) * 100, 2) if total > 0 else 0.0
        
        return {
            'paralelo_id': paralelo_id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'total_registros': total_registros,
            'total_presentes': total_presentes,
            'total_tarde': total_tarde,
            'total_ausente': total_ausente,
            'total_justificado': total_justificado,
            'porcentaje_asistencia': porcentaje_asistencia,
            'porcentaje_retrasos': porcentaje_retrasos,
        }
    
    async def obtener_estadisticas_sede(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de asistencia de una sede.
        
        Args:
            sede_id: ID de la sede
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            
        Returns:
            Diccionario con estadísticas globales de la sede
        """
        query = select(
            func.count(AsistenciaAlumno.id).label('total_registros'),
            func.count(
                case((AsistenciaAlumno.estado == 'presente', 1))
            ).label('total_presentes'),
            func.count(
                case((AsistenciaAlumno.estado == 'tarde', 1))
            ).label('total_tarde'),
            func.count(
                case((AsistenciaAlumno.estado == 'ausente', 1))
            ).label('total_ausente'),
            func.count(
                case((AsistenciaAlumno.estado == 'justificado', 1))
            ).label('total_justificado'),
        ).where(
            and_(
                AsistenciaAlumno.sede_id == sede_id,
                AsistenciaAlumno.fecha >= fecha_inicio,
                AsistenciaAlumno.fecha <= fecha_fin
            )
        )
        
        result = await self.session.execute(query)
        row = result.first()
        
        # Validar que row no sea None
        if not row:
            return {
                'sede_id': sede_id,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'total_registros': 0,
                'total_presentes': 0,
                'total_tarde': 0,
                'total_ausente': 0,
                'total_justificado': 0,
                'porcentaje_asistencia': 0.0,
                'porcentaje_retrasos': 0.0,
            }
        
        # Acceder por índice (orden del select)
        total_registros: int = row[0] or 0
        total_presentes: int = row[1] or 0
        total_tarde: int = row[2] or 0
        total_ausente: int = row[3] or 0
        total_justificado: int = row[4] or 0
        
        # Calcular porcentajes
        total = total_registros or 1
        porcentaje_asistencia = round((total_presentes / total) * 100, 2) if total > 0 else 0.0
        porcentaje_retrasos = round((total_tarde / total) * 100, 2) if total > 0 else 0.0
        
        return {
            'sede_id': sede_id,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'total_registros': total_registros,
            'total_presentes': total_presentes,
            'total_tarde': total_tarde,
            'total_ausente': total_ausente,
            'total_justificado': total_justificado,
            'porcentaje_asistencia': porcentaje_asistencia,
            'porcentaje_retrasos': porcentaje_retrasos,
        }
    
    async def obtener_retrasos(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        limite: int = 100
    ) -> Sequence[AsistenciaAlumno]:
        """Obtiene registros de retrasos (estado='tarde').
        
        Args:
            sede_id: ID de la sede
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            limite: Máximo de registros a retornar
            
        Returns:
            Secuencia de registros de asistencia con retrasos
        """
        query = select(AsistenciaAlumno).where(
            and_(
                AsistenciaAlumno.sede_id == sede_id,
                AsistenciaAlumno.fecha >= fecha_inicio,
                AsistenciaAlumno.fecha <= fecha_fin,
                AsistenciaAlumno.estado == 'tarde'
            )
        ).order_by(
            AsistenciaAlumno.fecha.desc()
            # Si tu modelo tiene hora_entrada, descomenta la siguiente línea:
            # AsistenciaAlumno.hora_entrada.asc()
        ).limit(limite)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def obtener_faltas(
        self,
        sede_id: int,
        fecha_inicio: date,
        fecha_fin: date,
        solo_sin_justificar: bool = False,
        limite: int = 100
    ) -> Sequence[AsistenciaAlumno]:
        """Obtiene registros de faltas.
        
        Args:
            sede_id: ID de la sede
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            solo_sin_justificar: Si True, solo ausencias sin justificar
            limite: Máximo de registros a retornar
            
        Returns:
            Secuencia de registros de asistencia con faltas
        """
        condiciones = [
            AsistenciaAlumno.sede_id == sede_id,
            AsistenciaAlumno.fecha >= fecha_inicio,
            AsistenciaAlumno.fecha <= fecha_fin,
        ]
        
        if solo_sin_justificar:
            # Solo ausencias sin justificar
            condiciones.append(AsistenciaAlumno.estado == 'ausente')
        else:
            # Ambas: ausente Y justificado
            condiciones.append(
                AsistenciaAlumno.estado.in_(['ausente', 'justificado'])
            )
        
        query = select(AsistenciaAlumno).where(
            and_(*condiciones)
        ).order_by(
            AsistenciaAlumno.fecha.desc()
        ).limit(limite)
        
        result = await self.session.execute(query)
        return result.scalars().all()
