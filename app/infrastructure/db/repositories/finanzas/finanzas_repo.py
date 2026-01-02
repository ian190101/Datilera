from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date

# Modelos
from app.infrastructure.db.models.finanzas.egresos import Egreso
from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum
from app.infrastructure.db.models.finanzas.categorias_egreso import CategoriaEgreso

class FinanzasRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def obtener_categoria_por_nombre(self, nombre: str, sede_id: int) -> CategoriaEgreso:
        """Busca una categoría (ej: 'Sueldos', 'Alquiler') o la crea si no existe"""
        stmt = select(CategoriaEgreso).where(
            and_(
                CategoriaEgreso.nombre.ilike(nombre),
                CategoriaEgreso.sede_id == sede_id
            )
        )
        result = await self.db.execute(stmt)
        categoria = result.scalar_one_or_none()
        
        if not categoria:
            categoria = CategoriaEgreso(nombre=nombre, sede_id=sede_id, descripcion="Categoría automática")
            self.db.add(categoria)
            await self.db.flush() # Para obtener el ID
            
        return categoria

    async def registrar_egreso(self, datos_egreso: dict, usuario_id: int) -> Egreso:
        """
        Registra un gasto y automáticamente lo impacta en el Libro de Caja.
        """
        # 1. Crear el registro en la tabla EGRESOS
        nuevo_egreso = Egreso(
            sede_id=datos_egreso["sede_id"],
            categoria_egreso_id=datos_egreso["categoria_id"],
            monto=datos_egreso["monto"],
            fecha_egreso=datos_egreso.get("fecha", date.today()),
            concepto=datos_egreso.get("concepto"),
            proveedor=datos_egreso.get("proveedor"), # Ej: Nombre del profesor o 'Ende'
            metodo_pago=datos_egreso.get("metodo_pago", "EFECTIVO"),
            numero_comprobante=datos_egreso.get("numero_comprobante"),
            observaciones=datos_egreso.get("observaciones"),
            registrado_por=usuario_id
        )
        
        self.db.add(nuevo_egreso)
        await self.db.flush()  # Obtenemos el ID del egreso recién creado

        # 2. Impactar automáticamente en LIBRO DE CAJA (La regla de oro del arqueo)
        movimiento_caja = LibroCaja(
            sede_id=datos_egreso["sede_id"],
            fecha=datos_egreso.get("fecha", date.today()),
            tipo=TipoMovimientoEnum.EGRESO,
            categoria_egreso_id=datos_egreso["categoria_id"],
            egreso_id=nuevo_egreso.id, # Vinculamos para trazabilidad
            monto=datos_egreso["monto"],
            concepto=f"Egreso: {datos_egreso.get('concepto')}",
            usuario_registro_id=usuario_id,
            # El saldo acumulado se recalcula en el reporte, o se puede calcular aquí si se requiere estricto
        )
        
        self.db.add(movimiento_caja)
        
        return nuevo_egreso