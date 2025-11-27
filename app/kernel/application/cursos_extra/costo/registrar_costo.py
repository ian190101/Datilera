# app/kernel/application/cursosextra/costo/registrar_costo.py

"""
Caso de Uso: Registrar Costo
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.kernel.domain.cursos_extra import (
    CostoCursoExtra,
    CostoCursoExtraRepositoryPort,
    CategoriaCostoCursoExtraRepositoryPort,
    IngresoCursoExtraRepositoryPort,
    CursoExtraRepositoryPort,
    CursoExtraNoEncontrado,
    CategoriaNoEncontrada,
    CategoriaInactiva,
    MontoInvalido,
)


class RegistrarCostoDTO:
    """DTO de entrada para registrar costo."""
    def __init__(
        self,
        curso_extra_id: int,
        categoria_costo_id: int,
        monto: Decimal,
        descripcion: Optional[str] = None,
        fecha_gasto: datetime = None,
        comprobante_url: Optional[str] = None,
        registrado_por_id: Optional[int] = None,
    ):
        self.curso_extra_id = curso_extra_id
        self.categoria_costo_id = categoria_costo_id
        self.monto = monto
        self.descripcion = descripcion
        self.fecha_gasto = fecha_gasto or datetime.utcnow()
        self.comprobante_url = comprobante_url
        self.registrado_por_id = registrado_por_id


class RegistrarCosto:
    """
    Caso de Uso: Registrar un costo/gasto de un curso extra.
    
    Validaciones:
    - El curso debe existir
    - La categoría debe existir y estar activa
    - El monto debe ser positivo
    - Actualiza automáticamente el registro de ingresos consolidados
    """
    
    def __init__(
        self,
        costo_repo: CostoCursoExtraRepositoryPort,
        categoria_repo: CategoriaCostoCursoExtraRepositoryPort,
        ingreso_repo: IngresoCursoExtraRepositoryPort,
        curso_repo: CursoExtraRepositoryPort,
    ):
        self.costo_repo = costo_repo
        self.categoria_repo = categoria_repo
        self.ingreso_repo = ingreso_repo
        self.curso_repo = curso_repo
    
    async def execute(self, dto: RegistrarCostoDTO) -> CostoCursoExtra:
        """Ejecuta el caso de uso."""
        
        # 1. Validar que el curso existe
        curso = await self.curso_repo.obtener_por_id(dto.curso_extra_id)
        if not curso:
            raise CursoExtraNoEncontrado(dto.curso_extra_id)
        
        # 2. Validar que la categoría existe y está activa
        categoria = await self.categoria_repo.obtener_por_id(dto.categoria_costo_id)
        if not categoria:
            raise CategoriaNoEncontrada(dto.categoria_costo_id)
        
        if not categoria.esta_activa():
            raise CategoriaInactiva(dto.categoria_costo_id)
        
        # 3. Validar monto
        if dto.monto <= Decimal("0"):
            raise MontoInvalido("El monto del costo debe ser mayor a 0.")
        
        # 4. Crear el costo
        costo = CostoCursoExtra(
            id=0,
            curso_extra_id=dto.curso_extra_id,
            categoria_costo_id=dto.categoria_costo_id,
            descripcion=dto.descripcion,
            monto=dto.monto,
            fecha_gasto=dto.fecha_gasto,
            comprobante_url=dto.comprobante_url,
        )
        
        costo_creado = await self.costo_repo.crear(costo)
        
        # 5. Actualizar gastos consolidados del curso
        total_gastos = await self.costo_repo.calcular_total_por_curso(dto.curso_extra_id)
        
        ingreso = await self.ingreso_repo.obtener_por_curso(dto.curso_extra_id)
        if ingreso:
            await self.ingreso_repo.actualizar_gastos(dto.curso_extra_id, total_gastos)
            # Recalcular ganancias
            await self.ingreso_repo.recalcular_ganancias(dto.curso_extra_id)
        
        return costo_creado
