# app/kernel/application/cursosextra/categoria_costo/crear_categoria_costo.py

"""
Caso de Uso: Crear Categoría de Costo
"""
from typing import Optional

from app.kernel.domain.cursos_extra import (
    CategoriaCostoCursoExtra,
    CategoriaCostoCursoExtraRepositoryPort,
    CursoExtraRepositoryPort,
    CursoExtraNoEncontrado,
    CategoriaDuplicada,
)


class CrearCategoriaCostoDTO:
    """DTO de entrada para crear categoría de costo."""
    def __init__(
        self,
        curso_extra_id: int,
        nombre: str,
        descripcion: Optional[str] = None,
        creado_por_id: Optional[int] = None,
    ):
        self.curso_extra_id = curso_extra_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.creado_por_id = creado_por_id


class CrearCategoriaCosto:
    """
    Caso de Uso: Crear una categoría dinámica de costo para un curso.
    
    Validaciones:
    - El curso debe existir
    - El nombre es obligatorio
    - No debe existir una categoría con el mismo nombre en el curso
    """
    
    def __init__(
        self,
        categoria_repo: CategoriaCostoCursoExtraRepositoryPort,
        curso_repo: CursoExtraRepositoryPort,
    ):
        self.categoria_repo = categoria_repo
        self.curso_repo = curso_repo
    
    async def execute(self, dto: CrearCategoriaCostoDTO) -> CategoriaCostoCursoExtra:
        """Ejecuta el caso de uso."""
        
        # Validar que el curso existe
        curso = await self.curso_repo.obtener_por_id(dto.curso_extra_id)
        if not curso:
            raise CursoExtraNoEncontrado(dto.curso_extra_id)
        
        # Validar nombre
        nombre = (dto.nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre de la categoría es obligatorio.")
        if len(nombre) > 100:
            raise ValueError("El nombre no puede superar 100 caracteres.")
        
        # Validar duplicados
        existe = await self.categoria_repo.existe_por_nombre(
            nombre=nombre,
            curso_id=dto.curso_extra_id
        )
        if existe:
            raise CategoriaDuplicada(nombre, dto.curso_extra_id)
        
        # Crear categoría
        categoria = CategoriaCostoCursoExtra(
            id=0,
            curso_extra_id=dto.curso_extra_id,
            nombre=nombre,
            descripcion=dto.descripcion,
            activo=True,
        )
        
        return await self.categoria_repo.crear(categoria)
