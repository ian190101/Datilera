# app/kernel/application/cursosextra/inscripcion/inscribir_alumno_externo.py

"""
Caso de Uso: Inscribir Alumno Externo a Curso Extra
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from app.kernel.domain.cursos_extra import (
    InscripcionCursoExtra,
    TipoAlumnoCursoExtra,
    EstadoInscripcionCursoExtra,
    BalanceCursoExtra,
    EstadoBalance,
    AlumnoExterno,
    CursoExtra,
    CursoExtraRepositoryPort,
    InscripcionCursoExtraRepositoryPort,
    BalanceCursoExtraRepositoryPort,
    AlumnoExternoRepositoryPort,
    CursoExtraNoEncontrado,
    CursoExtraInactivo,
    CuposAgotados,
    InscripcionDuplicada,
    AlumnoExternoNoEncontrado,
    DatosAlumnoIncompletos,
)


class InscribirAlumnoExternoDTO:
    """DTO de entrada para inscribir alumno externo."""
    def __init__(
        self,
        curso_extra_id: int,
        alumno_externo_id: Optional[int] = None,
        # Datos para crear alumno externo si no existe
        nombre_completo: Optional[str] = None,
        fecha_nacimiento: Optional[date] = None,
        edad_anios: Optional[int] = None,
        tutor_nombre: Optional[str] = None,
        tutor_celular: Optional[str] = None,
        tutor_email: Optional[str] = None,
        sede_id: Optional[int] = None,
        # Control
        fecha_inscripcion: date = None,
        inscrito_por_id: int = None,
    ):
        self.curso_extra_id = curso_extra_id
        self.alumno_externo_id = alumno_externo_id
        # Datos para crear alumno
        self.nombre_completo = nombre_completo
        self.fecha_nacimiento = fecha_nacimiento
        self.edad_anios = edad_anios
        self.tutor_nombre = tutor_nombre
        self.tutor_celular = tutor_celular
        self.tutor_email = tutor_email
        self.sede_id = sede_id
        # Control
        self.fecha_inscripcion = fecha_inscripcion or date.today()
        self.inscrito_por_id = inscrito_por_id


class InscribirAlumnoExterno:
    """
    Caso de Uso: Inscribir un alumno externo (no del centro) a un curso extra.
    
    Validaciones:
    - El curso debe existir y estar activo
    - Debe tener cupos disponibles
    - Si alumno_externo_id se proporciona, debe existir
    - Si no, se crea con los datos proporcionados
    - No debe existir una inscripción activa previa
    - Se crea automáticamente el balance con precio externo
    - Se incrementa el contador de inscritos del curso
    """
    
    def __init__(
        self,
        curso_repo: CursoExtraRepositoryPort,
        inscripcion_repo: InscripcionCursoExtraRepositoryPort,
        balance_repo: BalanceCursoExtraRepositoryPort,
        alumno_externo_repo: AlumnoExternoRepositoryPort,
    ):
        self.curso_repo = curso_repo
        self.inscripcion_repo = inscripcion_repo
        self.balance_repo = balance_repo
        self.alumno_externo_repo = alumno_externo_repo
    
    async def execute(self, dto: InscribirAlumnoExternoDTO) -> InscripcionCursoExtra:
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
        
        # 3. Obtener o crear alumno externo
        if dto.alumno_externo_id:
            # Usar alumno existente
            alumno_externo = await self.alumno_externo_repo.obtener_por_id(dto.alumno_externo_id)
            if not alumno_externo:
                raise AlumnoExternoNoEncontrado(dto.alumno_externo_id)
        else:
            # Crear nuevo alumno externo
            if not dto.nombre_completo or not dto.tutor_nombre or not dto.tutor_celular or not dto.sede_id:
                raise DatosAlumnoIncompletos(
                    "Para crear un alumno externo se requiere: nombre_completo, tutor_nombre, "
                    "tutor_celular y sede_id."
                )
            
            alumno_externo = AlumnoExterno(
                id=0,
                sede_id=dto.sede_id,
                nombre_completo=dto.nombre_completo,
                fecha_nacimiento=dto.fecha_nacimiento,
                edad_anios=dto.edad_anios,
                tutor_nombre=dto.tutor_nombre,
                tutor_celular=dto.tutor_celular,
                tutor_email=dto.tutor_email,
            )
            alumno_externo = await self.alumno_externo_repo.crear(alumno_externo)
        
        # 4. Validar que no existe inscripción activa previa
        existe = await self.inscripcion_repo.existe_inscripcion_activa(
            curso_id=dto.curso_extra_id,
            alumno_externo_id=alumno_externo.id
        )
        if existe:
            raise InscripcionDuplicada("externo", alumno_externo.id, dto.curso_extra_id)
        
        # 5. Crear inscripción
        inscripcion = InscripcionCursoExtra(
            id=0,
            curso_extra_id=dto.curso_extra_id,
            tipo_alumno=TipoAlumnoCursoExtra.EXTERNO,
            alumno_id=None,
            alumno_externo_id=alumno_externo.id,
            tutor_nombre=alumno_externo.tutor_nombre,
            tutor_celular=alumno_externo.tutor_celular,
            fecha_inscripcion=dto.fecha_inscripcion,
            estado=EstadoInscripcionCursoExtra.ACTIVO,
        )
        
        inscripcion_creada = await self.inscripcion_repo.crear(inscripcion)
        
        # 6. Crear balance con precio externo
        monto_total = curso.precio_externo
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
        
        # 7. Incrementar contador de inscritos
        await self.curso_repo.incrementar_inscritos(dto.curso_extra_id)
        
        return inscripcion_creada
