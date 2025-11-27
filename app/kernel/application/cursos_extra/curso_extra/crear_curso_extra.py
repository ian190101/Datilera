# app/kernel/application/cursosextra/curso_extra/crear_curso_extra.py

"""
Caso de Uso: Crear Curso Extra
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from app.kernel.domain.cursos_extra import (
    CursoExtra,
    CursoExtraRepositoryPort,
    IngresoCursoExtra,
    IngresoCursoExtraRepositoryPort,
    NombreCursoInvalido,
    InstructorInvalido,
    FechasInvalidas,
    PorcentajeInvalido,
    CupoMaximoInvalido,
    PrecioInvalido,
)


class CrearCursoExtraDTO:
    """DTO de entrada para crear curso extra."""
    def __init__(
        self,
        sede_id: int,
        nombre: str,
        instructor: str,
        gestion: int,
        fecha_inicio: date,
        cupo_maximo: int,
        precio_interno: Decimal,
        precio_externo: Decimal,
        descripcion: Optional[str] = None,
        fecha_fin: Optional[date] = None,
        porcentaje_institucion: Decimal = Decimal("50.00"),
        creado_por_id: Optional[int] = None,
    ):
        self.sede_id = sede_id
        self.nombre = nombre
        self.instructor = instructor
        self.gestion = gestion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.cupo_maximo = cupo_maximo
        self.precio_interno = precio_interno
        self.precio_externo = precio_externo
        self.porcentaje_institucion = porcentaje_institucion
        self.descripcion = descripcion
        self.creado_por_id = creado_por_id


class CrearCursoExtra:
    """
    Caso de Uso: Crear un nuevo curso extra.
    
    Validaciones:
    - Nombre y instructor obligatorios
    - Cupo máximo > 0
    - Porcentaje institución entre 0-100
    - Precios > 0
    - Fecha fin >= fecha inicio (si se proporciona)
    - Crea automáticamente el registro de ingresos consolidados
    """
    
    def __init__(
        self,
        curso_repo: CursoExtraRepositoryPort,
        ingreso_repo: IngresoCursoExtraRepositoryPort,
    ):
        self.curso_repo = curso_repo
        self.ingreso_repo = ingreso_repo
    
    async def execute(self, dto: CrearCursoExtraDTO) -> CursoExtra:
        """Ejecuta el caso de uso."""
        
        # Validación de nombre
        nombre = (dto.nombre or "").strip()
        if not nombre:
            raise NombreCursoInvalido("El nombre del curso es obligatorio.")
        if len(nombre) > 120:
            raise NombreCursoInvalido("El nombre no puede superar 120 caracteres.")
        
        # Validación de instructor
        instructor = (dto.instructor or "").strip()
        if not instructor:
            raise InstructorInvalido("El instructor es obligatorio.")
        if len(instructor) > 120:
            raise InstructorInvalido("El nombre del instructor no puede superar 120 caracteres.")
        
        # Validación de cupo máximo
        if dto.cupo_maximo <= 0:
            raise CupoMaximoInvalido(dto.cupo_maximo)
        
        # Validación de porcentaje
        if dto.porcentaje_institucion < Decimal("0") or dto.porcentaje_institucion > Decimal("100"):
            raise PorcentajeInvalido(float(dto.porcentaje_institucion))
        
        # Validación de precios
        if dto.precio_interno <= Decimal("0"):
            raise PrecioInvalido("El precio interno debe ser mayor a 0.")
        
        if dto.precio_externo <= Decimal("0"):
            raise PrecioInvalido("El precio externo debe ser mayor a 0.")
        
        # Validación de fechas
        if dto.fecha_fin is not None and dto.fecha_fin < dto.fecha_inicio:
            raise FechasInvalidas("La fecha de fin no puede ser anterior a la fecha de inicio.")
        
        # Crear entidad de dominio
        curso = CursoExtra(
            id=0,  # Se asignará por la BD
            sede_id=dto.sede_id,
            nombre=nombre,
            descripcion=dto.descripcion,
            instructor=instructor,
            gestion=dto.gestion,
            fecha_inicio=dto.fecha_inicio,
            fecha_fin=dto.fecha_fin,
            cupo_maximo=dto.cupo_maximo,
            inscritos_actuales=0,
            precio_interno=dto.precio_interno,
            precio_externo=dto.precio_externo,
            porcentaje_institucion=dto.porcentaje_institucion,
            activo=True,
        )
        
        # Persistir curso
        curso_creado = await self.curso_repo.crear(curso)
        
        # Crear registro de ingresos consolidados
        ingreso = IngresoCursoExtra(
            id=0,
            curso_extra_id=curso_creado.id,
            total_ingresos=Decimal("0.00"),
            total_gastos=Decimal("0.00"),
            ganancia_bruta=Decimal("0.00"),
            ganancia_institucion=Decimal("0.00"),
            ganancia_instructor=Decimal("0.00"),
        )
        await self.ingreso_repo.crear(ingreso)
        
        return curso_creado
