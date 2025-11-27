# app/kernel/application/cursosextra/curso_extra/actualizar_curso_extra.py

"""
Caso de Uso: Actualizar Curso Extra
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from app.kernel.domain.cursos_extra import (
    CursoExtra,
    CursoExtraRepositoryPort,
    CursoExtraNoEncontrado,
    NombreCursoInvalido,
    InstructorInvalido,
    FechasInvalidas,
    PorcentajeInvalido,
    CupoMaximoInvalido,
    PrecioInvalido,
)


class ActualizarCursoExtraDTO:
    """DTO de entrada para actualizar curso extra."""
    def __init__(
        self,
        curso_id: int,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        instructor: Optional[str] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        cupo_maximo: Optional[int] = None,
        precio_interno: Optional[Decimal] = None,
        precio_externo: Optional[Decimal] = None,
        porcentaje_institucion: Optional[Decimal] = None,
    ):
        self.curso_id = curso_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.instructor = instructor
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.cupo_maximo = cupo_maximo
        self.precio_interno = precio_interno
        self.precio_externo = precio_externo
        self.porcentaje_institucion = porcentaje_institucion


class ActualizarCursoExtra:
    """
    Caso de Uso: Actualizar un curso extra existente.
    
    Validaciones:
    - El curso debe existir
    - No se puede reducir cupo_maximo por debajo de inscritos_actuales
    - Validaciones de formato para campos modificados
    """
    
    def __init__(self, curso_repo: CursoExtraRepositoryPort):
        self.curso_repo = curso_repo
    
    async def execute(self, dto: ActualizarCursoExtraDTO) -> CursoExtra:
        """Ejecuta el caso de uso."""
        
        # Obtener curso existente
        curso = await self.curso_repo.obtener_por_id(dto.curso_id)
        if not curso:
            raise CursoExtraNoEncontrado(dto.curso_id)
        
        # Actualizar campos si se proporcionan
        if dto.nombre is not None:
            nombre = dto.nombre.strip()
            if not nombre:
                raise NombreCursoInvalido("El nombre no puede estar vacío.")
            if len(nombre) > 120:
                raise NombreCursoInvalido("El nombre no puede superar 120 caracteres.")
            curso.nombre = nombre
        
        if dto.descripcion is not None:
            curso.descripcion = dto.descripcion
        
        if dto.instructor is not None:
            instructor = dto.instructor.strip()
            if not instructor:
                raise InstructorInvalido("El instructor no puede estar vacío.")
            if len(instructor) > 120:
                raise InstructorInvalido("El instructor no puede superar 120 caracteres.")
            curso.instructor = instructor
        
        if dto.cupo_maximo is not None:
            if dto.cupo_maximo <= 0:
                raise CupoMaximoInvalido(dto.cupo_maximo)
            
            # Validación: no reducir cupo por debajo de inscritos actuales
            if dto.cupo_maximo < curso.inscritos_actuales:
                raise CupoMaximoInvalido(
                    f"No se puede reducir el cupo máximo a {dto.cupo_maximo} "
                    f"porque ya hay {curso.inscritos_actuales} inscritos."
                )
            curso.cupo_maximo = dto.cupo_maximo
        
        if dto.precio_interno is not None:
            if dto.precio_interno <= Decimal("0"):
                raise PrecioInvalido("El precio interno debe ser mayor a 0.")
            curso.precio_interno = dto.precio_interno
        
        if dto.precio_externo is not None:
            if dto.precio_externo <= Decimal("0"):
                raise PrecioInvalido("El precio externo debe ser mayor a 0.")
            curso.precio_externo = dto.precio_externo
        
        if dto.porcentaje_institucion is not None:
            if dto.porcentaje_institucion < Decimal("0") or dto.porcentaje_institucion > Decimal("100"):
                raise PorcentajeInvalido(float(dto.porcentaje_institucion))
            curso.porcentaje_institucion = dto.porcentaje_institucion
        
        if dto.fecha_inicio is not None:
            curso.fecha_inicio = dto.fecha_inicio
        
        if dto.fecha_fin is not None:
            curso.fecha_fin = dto.fecha_fin
        
        # Validar coherencia de fechas
        if curso.fecha_fin is not None and curso.fecha_fin < curso.fecha_inicio:
            raise FechasInvalidas("La fecha de fin no puede ser anterior a la fecha de inicio.")
        
        # Persistir cambios
        return await self.curso_repo.guardar(curso)
