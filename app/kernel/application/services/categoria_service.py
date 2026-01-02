from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.db.models.finanzas.categorias_pago import CategoriaPago
from app.infrastructure.db.models.finanzas.categorias_egreso import CategoriaEgreso

class CategoriasService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar_categorias(self, sede_id: int):
        stmt_pagos = select(CategoriaPago).where(CategoriaPago.sede_id == sede_id)
        stmt_egresos = select(CategoriaEgreso).where(CategoriaEgreso.sede_id == sede_id)
        
        pagos = (await self.db.execute(stmt_pagos)).scalars().all()
        egresos = (await self.db.execute(stmt_egresos)).scalars().all()
        
        return {
            "ingresos": [{"id": c.id, "nombre": c.nombre} for c in pagos],
            "egresos": [{"id": c.id, "nombre": c.nombre} for c in egresos]
        }

    async def crear_categoria_ingreso(self, nombre: str, sede_id: int):
        nueva = CategoriaPago(nombre=nombre, sede_id=sede_id, activo=True)
        self.db.add(nueva)
        return nueva

    async def crear_categoria_egreso(self, nombre: str, sede_id: int):
        nueva = CategoriaEgreso(nombre=nombre, sede_id=sede_id, activo=True)
        self.db.add(nueva)
        return nueva