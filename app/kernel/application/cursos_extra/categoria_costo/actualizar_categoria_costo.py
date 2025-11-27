# app/kernel/application/cursosextra/categoria_costo/actualizar_categoria_costo.py

"""
Caso de Uso: Actualizar Categoría de Costo
"""
from typing import Optional

from app.kernel.domain.cursos_extra import (
    CategoriaCostoCursoExtra,
    CategoriaCostoCursoExtraRepositoryPort,
    CategoriaNoEncontrada,
    CategoriaDuplicada,
)


class ActualizarCategoriaCostoDTO:
    """DTO de entrada para actualizar categoría de costo."""
    def __init__(
        self,
        categoria_id: int,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
    ):
        self.categoria_id = categoria_id
        self.nombre = nombre
        self.descripcion = descripcion


class ActualizarCategoriaCosto:
    """
    Caso de Uso: Actualizar una categoría de costo existente.
    
    Validaciones:
    - La categoría debe existir
    - Si se actualiza el nombre, no debe duplicarse
    """
    
    def __init__(self, categoria_repo: CategoriaCostoCursoExtraRepositoryPort):
        self.categoria_repo = categoria_repo
    
    async def execute(self, dto: ActualizarCategoriaCostoDTO) -> CategoriaCostoCursoExtra:
        """Ejecuta el caso de uso."""
        
        # Obtener categoría existente
        categoria = await self.categoria_repo.obtener_por_id(dto.categoria_id)
        if not categoria:
            raise CategoriaNoEncontrada(dto.categoria_id)
        
        # Actualizar campos si se proporcionan
        if dto.nombre is not None:
            nombre = dto.nombre.strip()
            if not nombre:
                raise ValueError("El nombre no puede estar vacío.")
            if len(nombre) > 100:
                raise ValueError("El nombre no puede superar 100 caracteres.")
            
            # Validar duplicados (excluyendo la categoría actual)
            existe = await self.categoria_repo.existe_por_nombre(
                nombre=nombre,
                curso_id=categoria.curso_extra_id,
                excluir_id=dto.categoria_id
            )
            if existe:
                raise CategoriaDuplicada(nombre, categoria.curso_extra_id)
            
            categoria.actualizar_nombre(nombre)
        
        if dto.descripcion is not None:
            categoria.descripcion = dto.descripcion
        
        # Persistir cambios
        return await self.categoria_repo.guardar(categoria)
