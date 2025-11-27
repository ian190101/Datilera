# app/kernel/application/cursosextra/costo/eliminar_costo.py

"""
Caso de Uso: Eliminar Costo
"""
from app.kernel.domain.cursos_extra import (
    CostoCursoExtraRepositoryPort,
    IngresoCursoExtraRepositoryPort,
    CostoNoEncontrado,
)


class EliminarCosto:
    """
    Caso de Uso: Eliminar un costo.
    
    Validaciones:
    - El costo debe existir
    - Recalcula automáticamente los gastos consolidados
    """
    
    def __init__(
        self,
        costo_repo: CostoCursoExtraRepositoryPort,
        ingreso_repo: IngresoCursoExtraRepositoryPort,
    ):
        self.costo_repo = costo_repo
        self.ingreso_repo = ingreso_repo
    
    async def execute(self, costo_id: int) -> bool:
        """Ejecuta el caso de uso."""
        
        # Obtener costo para saber el curso_id
        costo = await self.costo_repo.obtener_por_id(costo_id)
        if not costo:
            raise CostoNoEncontrado(costo_id)
        
        curso_id = costo.curso_extra_id
        
        # Eliminar costo
        eliminado = await self.costo_repo.eliminar(costo_id)
        
        if eliminado:
            # Recalcular gastos consolidados
            total_gastos = await self.costo_repo.calcular_total_por_curso(curso_id)
            await self.ingreso_repo.actualizar_gastos(curso_id, total_gastos)
            await self.ingreso_repo.recalcular_ganancias(curso_id)
        
        return eliminado
