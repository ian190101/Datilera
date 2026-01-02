from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.repositories.finanzas.finanzas_repo import FinanzasRepository
from datetime import date

class FinanzasService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FinanzasRepository(db)

    async def registrar_gasto_operativo(self, datos: dict, usuario_id: int):
        """
        Maneja Gastos Fijos (Luz, Agua) y Variables (Materiales, Almuerzos).
        Basado en archivos: GF.csv, G ALMU.csv, MYM.csv
        """
        # 1. Obtener o crear la categoría correcta
        # Ej: Si viene "Alquiler", buscamos esa categoría.
        categoria = await self.repo.obtener_categoria_por_nombre(datos["categoria_nombre"], datos["sede_id"])
        
        datos_egreso = {
            "sede_id": datos["sede_id"],
            "categoria_id": categoria.id,
            "monto": datos["monto"],
            "fecha": datos.get("fecha", date.today()),
            "concepto": datos.get("detalle"), # Ej: "Rendición #12"
            "proveedor": datos.get("proveedor"), # Ej: "EMSA", "Comedor"
            "metodo_pago": datos.get("metodo_pago", "EFECTIVO"),
            "numero_comprobante": datos.get("comprobante"),
            "observaciones": datos.get("observaciones")
        }

        # 2. Guardar
        return await self.repo.registrar_egreso(datos_egreso, usuario_id)

    async def registrar_pago_sueldo(self, datos_sueldo: dict, usuario_id: int):
        """
        Maneja la lógica de la hoja SUELDOS.csv
        Calcula el COSTO TOTAL para la empresa (Sueldo + Seguro)
        """
        # Según tu Excel: Total = Liquido Pagable + Seguro
        # Si el sueldo base es 3500 y seguro 143.28 -> Total Egreso = 3643.28
        
        sueldo_liquido = float(datos_sueldo.get("liquido_pagable", 0))
        seguro = float(datos_sueldo.get("seguro", 0))
        bonos = float(datos_sueldo.get("bonos", 0))
        descuentos = float(datos_sueldo.get("descuentos_faltas", 0))
        
        # El egreso real de caja es lo que sale efectivamente + lo que se paga al seguro
        # Asumimos que el "Total" del excel es el costo total empresa que sale de caja
        monto_total = sueldo_liquido + seguro + bonos - descuentos

        # Categoría automática "Sueldos y Salarios"
        categoria = await self.repo.obtener_categoria_por_nombre("Sueldos y Salarios", datos_sueldo["sede_id"])

        # Armamos el detalle para que quede en observaciones (Auditoría)
        detalle_texto = (
            f"Sueldo: {datos_sueldo.get('nombre_empleado')} | "
            f"Cargo: {datos_sueldo.get('cargo')} | "
            f"Líquido: {sueldo_liquido} | Seguro: {seguro}"
        )

        datos_egreso = {
            "sede_id": datos_sueldo["sede_id"],
            "categoria_id": categoria.id,
            "monto": monto_total,
            "fecha": datos_sueldo.get("fecha_pago", date.today()),
            "concepto": f"Pago Sueldo - {datos_sueldo.get('mes_pagado', 'Mes Actual')}",
            "proveedor": datos_sueldo.get("nombre_empleado"), # El empleado es el proveedor del servicio
            "metodo_pago": datos_sueldo.get("metodo_pago", "EFECTIVO"),
            "observaciones": detalle_texto
        }

        return await self.repo.registrar_egreso(datos_egreso, usuario_id)