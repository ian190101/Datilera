# app/kernel/application/cursosextra/costo/actualizar_costo.py

"""
Caso de Uso: Actualizar Costo
"""
from decimal import Decimal
from typing import Optional

from app.kernel.domain.cursos_extra import (
    CostoCursoExtra,
    CostoCursoExtraRepositoryPort,
    IngresoCursoExtraRepositoryPort,
    CostoNoEncontrado,
    MontoInvalido,
)


class ActualizarCostoDTO:
    """DTO de entrada para actualizar costo."""
    def __init__(
        self,
        costo_id: int,
        monto: Optional[Decimal] = None,
        descripcion: Optional[str] = None,
        comprobante_url: Optional[str] = None,
    ):
        self.costo_id = costo_id
        self.monto = monto
        self.descripcion = descripcion
        self.comprobante_url = comprobante_url


class ActualizarCosto:
    """
    Caso de Uso: Actualizar un costo existente.
    
    Validaciones:
    - El costo debe existir
    - Si se actualiza el monto, debe ser positivo
    - Recalcula automáticamente los gastos consolidados
    """
    
    def __init__(
        self,
        costo_repo: CostoCursoExtraRepositoryPort,
        ingreso_repo: IngresoCursoExtraRepositoryPort,
    ):
        self.costo_repo = costo_repo
        self.ingreso_repo = ingreso_repo
    
    async def execute(self, dto: ActualizarCostoDTO) -> CostoCursoExtra:
        """Ejecuta el caso de uso."""
        
        # Obtener costo existente
        costo = await self.costo_repo.obtener_por_id(dto.costo_id)
        if not costo:
            raise CostoNoEncontrado(dto.costo_id)
        
        # Actualizar campos si se proporcionan
        if dto.monto is not None:
            if dto.monto <= Decimal("0"):
                raise MontoInvalido("El monto debe ser mayor a 0.")
            costo.actualizar_monto(dto.monto)
        
        if dto.descripcion is not None:
            costo.actualizar_descripcion(dto.descripcion)
        
        if dto.comprobante_url is not None:
            costo.comprobante_url = dto.comprobante_url
        
        # Persistir cambios
        costo_actualizado = await self.costo_repo.guardar(costo)
        
        # Recalcular gastos consolidados
        total_gastos = await self.costo_repo.calcular_total_por_curso(costo.curso_extra_id)
        await self.ingreso_repo.actualizar_gastos(costo.curso_extra_id, total_gastos)
        await self.ingreso_repo.recalcular_ganancias(costo.curso_extra_id)
        
        return costo_actualizado
