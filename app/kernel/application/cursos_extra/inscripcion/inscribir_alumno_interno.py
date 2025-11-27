# app/kernel/application/cursosextra/inscripcion/inscribir_alumno_interno.py

"""
Caso de Uso: Inscribir Alumno Interno a Curso Extra
"""
from datetime import date
from decimal import Decimal

from app.kernel.domain.cursos_extra import (
    InscripcionCursoExtra,
    TipoAlumnoCursoExtra,
    EstadoInscripcionCursoExtra,
    BalanceCursoExtra,
    EstadoBalance,
    CursoExtra,
    CursoExtraRepositoryPort,
    InscripcionCursoExtraRepositoryPort,
    BalanceCursoExtraRepositoryPort,
    CursoExtraNoEncontrado,
    CursoExtraInactivo,
    CuposAgotados,
    InscripcionDuplicada,
)


class InscribirAlumnoInternoDTO:
    """DTO de entrada para inscribir alumno interno."""
    def __init__(
        self,
        curso_extra_id: int,
        alumno_id: int,
        fecha_inscripcion: date = None,
        inscrito_por_id: int = None,
    ):
        self.curso_extra_id = curso_extra_id
        self.alumno_id = alumno_id
        self.fecha_inscripcion = fecha_inscripcion or date.today()
        self.inscrito_por_id = inscrito_por_id


class InscribirAlumnoInterno:
    """
    Caso de Uso: Inscribir un alumno interno (del centro) a un curso extra.
    
    Validaciones:
    - El curso debe existir y estar activo
    - Debe tener cupos disponibles
    - No debe existir una inscripción activa previa
    - Se crea automáticamente el balance con precio interno
    - Se incrementa el contador de inscritos del curso
    """
    
    def __init__(
        self,
        curso_repo: CursoExtraRepositoryPort,
        inscripcion_repo: InscripcionCursoExtraRepositoryPort,
        balance_repo: BalanceCursoExtraRepositoryPort,
    ):
        self.curso_repo = curso_repo
        self.inscripcion_repo = inscripcion_repo
        self.balance_repo = balance_repo
    
    async def execute(self, dto: InscribirAlumnoInternoDTO) -> InscripcionCursoExtra:
        """Ejecuta el caso de uso."""
        
        # 1. Validar que el curso existe y está activo
        curso = await self.curso_repo.obtener_por_id(dto.curso_extra_id)
        if not curso:
            raise CursoExtraNoEncontrado(dto.curso_extra_id)
        
        if not curso.esta_activo():
            raise CursoExtraInactivo(dto.curso_extra_id)
        
        # 2. Validar cupos disponibles
        if not curso.tiene_cupos_disponibles():
            raise CuposAgotados(dto.curso_extra_id, curso.nombre)
        
        # 3. Validar que no existe inscripción activa previa
        existe = await self.inscripcion_repo.existe_inscripcion_activa(
            curso_id=dto.curso_extra_id,
            alumno_id=dto.alumno_id
        )
        if existe:
            raise InscripcionDuplicada("interno", dto.alumno_id, dto.curso_extra_id)
        
        # 4. Crear inscripción
        inscripcion = InscripcionCursoExtra(
            id=0,
            curso_extra_id=dto.curso_extra_id,
            tipo_alumno=TipoAlumnoCursoExtra.INTERNO,
            alumno_id=dto.alumno_id,
            alumno_externo_id=None,
            tutor_nombre=None,
            tutor_celular=None,
            fecha_inscripcion=dto.fecha_inscripcion,
            estado=EstadoInscripcionCursoExtra.ACTIVO,
        )
        
        inscripcion_creada = await self.inscripcion_repo.crear(inscripcion)
        
        # 5. Crear balance con precio interno
        monto_total = curso.precio_interno
        balance = BalanceCursoExtra(
            id=0,
            inscripcion_curso_extra_id=inscripcion_creada.id,
            monto_total=monto_total,
            monto_pagado=Decimal("0.00"),
            saldo=monto_total,
            fecha_vencimiento=None,
            estado=EstadoBalance.PENDIENTE,
        )
        await self.balance_repo.crear(balance)
        
        # 6. Incrementar contador de inscritos
        await self.curso_repo.incrementar_inscritos(dto.curso_extra_id)
        
        return inscripcion_creada
