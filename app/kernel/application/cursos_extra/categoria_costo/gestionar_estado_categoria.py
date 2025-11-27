# app/kernel/application/cursosextra/categoria_costo/gestionar_estado_categoria.py

"""
Caso de Uso: Gestionar Estado de Categoría de Costo
"""
from app.kernel.domain.cursos_extra import (
    CategoriaCostoCursoExtra,
    CategoriaCostoCursoExtraRepositoryPort,
    CategoriaNoEncontrada,
)


class GestionarEstadoCategoria:
    """
    Caso de Uso: Activar o desactivar una categoría de costo.
    
    Reglas:
    - Una categoría desactivada no permite registrar nuevos costos
    - Los costos existentes se mantienen
    """
    
    def __init__(self, categoria_repo: CategoriaCostoCursoExtraRepositoryPort):
        self.categoria_repo = categoria_repo
    
    async def activar(self, categoria_id: int) -> CategoriaCostoCursoExtra:
        """Activa una categoría."""
        categoria = await self.categoria_repo.obtener_por_id(categoria_id)
        if not categoria:
            raise CategoriaNoEncontrada(categoria_id)
        
        return await self.categoria_repo.activar_desactivar(categoria_id, True)
    
    async def desactivar(self, categoria_id: int) -> CategoriaCostoCursoExtra:
        """Desactiva una categoría."""
        categoria = await self.categoria_repo.obtener_por_id(categoria_id)
        if not categoria:
            raise CategoriaNoEncontrada(categoria_id)
        
        return await self.categoria_repo.activar_desactivar(categoria_id, False)
