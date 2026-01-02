from datetime import date, timedelta, datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func


# Modelos
from app.infrastructure.db.models.finanzas.plan_pago_personalizado import PlanPagoPersonalizado
from app.infrastructure.db.models.finanzas.cuota_plan_pago import CuotaPlanPago
from app.infrastructure.db.models.finanzas.prorrateo import Prorrateo
from app.infrastructure.db.models.finanzas.descuento import Descuento
from app.infrastructure.db.models.finanzas.pagos import Pago
from app.infrastructure.db.models.finanzas.libro_caja import LibroCaja, TipoMovimientoEnum
from app.infrastructure.db.models.finanzas.comprobantes import Comprobante
from app.infrastructure.db.models.alumnos.alumnos import Alumno


# Repositorios (Reutilizamos el de finanzas para el Libro Caja)
from app.infrastructure.db.repositories.finanzas.finanzas_repo import FinanzasRepository


class IngresosService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.finanzas_repo = FinanzasRepository(db)


    # =================================================================
    # 🧠 REGLA DE NEGOCIO 1: PRORRATEO (Historias de Usuario )
    # =================================================================
    def calcular_prorrateo_ingreso(self, fecha_ingreso: date, mensualidad_base: float) -> dict:
        """
        Calcula el monto del primer mes basado en la regla de los 20 días hábiles.
        Regla: Si faltan 3 días o menos para fin de mes, se cobra desde el siguiente.
        """
        # 1. Determinar si pasa al siguiente mes (Regla de los 3 días)
        # Simplificación: Si es día > 27, asumimos que pasa al siguiente mes
        # (Para ser exactos con días hábiles se requeriría un calendario de feriados,
        # pero esta es la aproximación estándar administrativa).
        _, last_day = self._get_month_range(fecha_ingreso)
        dias_restantes = last_day - fecha_ingreso.day

        if dias_restantes <= 3:
            return {
                "aplica_prorrateo": False,
                "fecha_inicio_cobro": self._get_first_day_next_month(fecha_ingreso),
                "monto_primer_pago": Decimal(mensualidad_base),
                "mensaje": "Inscripción al cierre de mes. El cobro inicia el mes siguiente."
            }


        # 2. Cálculo del Prorrateo (Regla de los 20 días)
        # "Siempre se tomará en cuenta 20 días hábiles"
        costo_diario = mensualidad_base / 20

        # Calculamos días hábiles restantes (Lunes a Viernes) desde la fecha de ingreso
        dias_habiles_asistencia = self._contar_dias_habiles_restantes(fecha_ingreso)

        # Si los días hábiles superan 20 (caso raro), topeamos a 20
        dias_a_cobrar = min(dias_habiles_asistencia, 20)

        monto_prorrateado = round(costo_diario * dias_a_cobrar, 2) # Redondeo estándar


        return {
            "aplica_prorrateo": True,
            "fecha_inicio_cobro": fecha_ingreso,
            "dias_cobrados": dias_a_cobrar,
            "monto_primer_pago": Decimal(monto_prorrateado),
            "mensaje": f"Prorrateo aplicado: {dias_a_cobrar} días hábiles x {costo_diario:.2f} Bs."
        }


    # =================================================================
    # 🧠 REGLA DE NEGOCIO 2: GENERACIÓN DE PLAN (Mensualidad + Material)
    # =================================================================
    async def generar_plan_anual(self, datos_plan: dict, usuario_id: int):
        """
        Genera el PlanPagoPersonalizado y sus 12 (o menos) cuotas.
        Maneja descuentos por pago anual/semestral .
        """
        # 1. Crear la cabecera del Plan
        nuevo_plan = PlanPagoPersonalizado(
            alumno_id=datos_plan["alumno_id"],
            sede_id=datos_plan["sede_id"],
            monto_base=datos_plan["mensualidad"], # Ej: 950
            incluye_material=datos_plan.get("incluye_material", False),
            monto_material=datos_plan.get("monto_material", 0), # Ej: 3400
            fecha_inicio=datos_plan["fecha_inicio"],
            creado_por=usuario_id
        )
        self.db.add(nuevo_plan)
        await self.db.flush()


        # 2. Aplicar Descuentos Globales (Si corresponde)
        descuento_aplicado = 0
        if datos_plan.get("tipo_pago") == "ANUAL":
            descuento_aplicado = 0.06 # 6%
        elif datos_plan.get("tipo_pago") == "SEMESTRAL":
            descuento_aplicado = 0.03 # 3%


        # 3. Generar las Cuotas (Mensualidades)
        # Empezamos desde el mes de la fecha de inicio de cobro
        fecha_cursor = datos_plan["fecha_inicio_cobro"]
        meses_restantes = 12 - fecha_cursor.month + 1 # Aprox hasta fin de año (diciembre)

        cuotas_a_generar = []

        # A) Cuota 1 (Puede ser prorrateada)
        monto_mes_1 = datos_plan["monto_primer_pago"] # Ya viene calculada del prorrateo
        if descuento_aplicado > 0:
            monto_mes_1 = monto_mes_1 * Decimal(1 - descuento_aplicado)


        cuota_1 = CuotaPlanPago(
            plan_id=nuevo_plan.id,
            numero_cuota=1,
            monto_cuota=monto_mes_1,
            fecha_vencimiento=fecha_cursor.replace(day=10), # Vence el 10
            estado="pendiente"
        )
        cuotas_a_generar.append(cuota_1)


        # B) Resto de Cuotas
        for i in range(1, meses_restantes):
            # Avanzar al siguiente mes
            mes_siguiente = (fecha_cursor.month + i - 1) % 12 + 1
            anio_siguiente = fecha_cursor.year + ((fecha_cursor.month + i - 1) // 12)

            # Si pasamos de diciembre, paramos (gestión escolar)
            # Regla : "El año se toma en cuenta hasta antes de navidad"
            if mes_siguiente == 1 and i > 0:
                break


            fecha_venc = date(anio_siguiente, mes_siguiente, 10)

            monto_cuota = Decimal(datos_plan["mensualidad"])
            if descuento_aplicado > 0:
                monto_cuota = monto_cuota * Decimal(1 - descuento_aplicado)


            cuota = CuotaPlanPago(
                plan_id=nuevo_plan.id,
                numero_cuota=i+1,
                monto_cuota=monto_cuota,
                fecha_vencimiento=fecha_venc,
                estado="pendiente"
            )
            cuotas_a_generar.append(cuota)


        self.db.add_all(cuotas_a_generar)

        # 4. Generar Cuota de Material/Merienda (Pago Único o Dividido)
        # "Se puede pagar cuota inicial del 40% o dividir"
        # Aquí simplificamos creando una "Cuota Especial" o varias.
        if nuevo_plan.incluye_material:
            cuota_material = CuotaPlanPago(
                plan_id=nuevo_plan.id,
                numero_cuota=99, # 99 indica Materiales
                monto_cuota=nuevo_plan.monto_material,
                fecha_vencimiento=datos_plan["fecha_inicio"], # Se paga al inicio
                estado="pendiente"
            )
            self.db.add(cuota_material)


        return nuevo_plan


    # =================================================================
    # 🧠 REGLA DE NEGOCIO 3: REGISTRO DE COBRO (Ingreso Real)
    # =================================================================
    async def registrar_pago_mensualidad(self, datos_pago: dict, usuario_id: int):
        """
        Registra el pago y vincula el comprobante (archivo) si existe.
        """
        # 1. Buscar cuota y validar (Igual que antes)
        cuota = await self.db.get(CuotaPlanPago, datos_pago["cuota_id"])
        if not cuota: raise ValueError("Cuota no encontrada")


        monto_pagado = Decimal(datos_pago["monto"])

        # 2. Registrar el Pago
        nuevo_pago = Pago(
            alumno_id=datos_pago["alumno_id"],
            categoria_pago_id=datos_pago["categoria_id"],
            monto_pagado=monto_pagado,
            fecha_pago=datos_pago.get("fecha", date.today()),
            metodo_pago=datos_pago["metodo_pago"], # QR, EFECTIVO, etc.
            numero_comprobante=datos_pago.get("numero_referencia"), # El código del banco
            registrado_por=usuario_id
        )
        self.db.add(nuevo_pago)
        await self.db.flush() # Para tener el ID del pago


        # 3. GUARDAR EL ARCHIVO DEL COMPROBANTE (NUEVO)
        # Si nos pasaron una URL de archivo (porque fue QR o Transferencia)
        if datos_pago.get("comprobante_url"):
            nuevo_comprobante = Comprobante(
                pago_id=nuevo_pago.id,
                url=datos_pago["comprobante_url"],
                nombre_archivo=datos_pago.get("comprobante_nombre", "comprobante.jpg")
            )
            self.db.add(nuevo_comprobante)


        # 4. Actualizar Cuota y Libro Caja (Igual que antes)
        cuota.monto_pagado += monto_pagado
        cuota.fecha_pago = datetime.now()
        cuota.pago_id = nuevo_pago.id

        if cuota.monto_pagado >= cuota.monto_cuota:
            cuota.estado = "pagado"
        else:
            cuota.estado = "parcial"


        movimiento = LibroCaja(
            sede_id=datos_pago["sede_id"],
            fecha=datos_pago.get("fecha", date.today()),
            tipo=TipoMovimientoEnum.INGRESO,
            categoria_pago_id=datos_pago["categoria_id"],
            pago_id=nuevo_pago.id, # Vinculamos al pago
            monto=monto_pagado,
            concepto=f"Pago Cuota {cuota.numero_cuota} - {datos_pago['nombre_alumno']}",
            usuario_registro_id=usuario_id
        )
        self.db.add(movimiento)


        return nuevo_pago



    # --- Helpers ---
    def _contar_dias_habiles_restantes(self, fecha: date) -> int:
        """Cuenta Lunes-Viernes desde fecha hasta fin de mes"""
        _, last_day = self._get_month_range(fecha)
        dias_habiles = 0
        current = fecha
        while current.day <= last_day and current.month == fecha.month:
            if current.weekday() < 5: # 0=Lunes, 4=Viernes
                dias_habiles += 1
            current += timedelta(days=1)
        return dias_habiles


    def _get_month_range(self, d: date):
        import calendar
        return calendar.monthrange(d.year, d.month)


    def _get_first_day_next_month(self, d: date):
        if d.month == 12:
            return date(d.year + 1, 1, 1)
        else:
            return date(d.year, d.month + 1, 1)




    # ... (métodos anteriores de IngresosService) ...


    async def anular_pago(self, pago_id: int, usuario_id: int, motivo: str):
        """
        Revierte un pago realizado:
        1. Marca el pago como anulado.
        2. Resta el monto de la Cuota (vuelve a estar pendiente).
        3. Crea un contra-asiento en Libro Caja (Ingreso Negativo) para ajustar el arqueo.
        """
        # 1. Obtener el Pago con sus relaciones
        # Necesitamos saber qué cuota pagó para restaurar la deuda
        stmt = select(Pago).where(Pago.id == pago_id)
        result = await self.db.execute(stmt)
        pago = result.scalar_one_or_none()


        if not pago:
            raise ValueError(f"El pago {pago_id} no existe.")

        if pago.anulado:
            raise ValueError("Este pago ya fue anulado anteriormente.")


        # 2. Marcar como Anulado (Auditoría)
        pago.anulado = True
        pago.anulado_por = usuario_id
        pago.anulado_en = datetime.now()
        pago.motivo_anulacion = motivo


        # 3. Restaurar la Deuda en la Cuota
        # Buscamos la cuota vinculada a este pago
        # NOTA: Como un pago puede cubrir una cuota parcial o total,
        # debemos buscar la cuota que tenga este pago_id.
        # (Si tu modelo CuotaPlanPago tiene relación directa, úsala).
        stmt_cuota = select(CuotaPlanPago).where(CuotaPlanPago.pago_id == pago.id)
        result_cuota = await self.db.execute(stmt_cuota)
        cuota = result_cuota.scalar_one_or_none()


        if cuota:
            # Restamos lo que se había pagado
            cuota.monto_pagado -= pago.monto_pagado

            # Recalcular estado
            if cuota.monto_pagado <= 0:
                cuota.estado = "pendiente"
                cuota.monto_pagado = Decimal(0) # Evitar negativos por decimales
                cuota.pago_id = None # Desvinculamos si quedó en 0
            else:
                cuota.estado = "parcial"
        else:
            # Si no hay cuota vinculada directa (ej: pago agrupado),
            # podrías requerir lógica extra, pero por ahora asumimos 1 a 1.
            pass


        # 4. Ajustar Libro de Caja (Contra-asiento)
        # Insertamos un registro idéntico pero con monto NEGATIVO.
        # Al sumar el arqueo: 100 (original) + (-100) (anulación) = 0.
        contra_asiento = LibroCaja(
            sede_id=None,  # O pasar sede_id como param
            fecha=date.today(), # La anulación impacta la caja de HOY, no la del día del pago original
            tipo=TipoMovimientoEnum.INGRESO, # Mantenemos tipo Ingreso
            categoria_pago_id=pago.categoria_pago_id,
            pago_id=pago.id,
            monto=-pago.monto_pagado, # <--- LA CLAVE: Monto negativo
            concepto=f"ANULACIÓN Pago #{pago.id} - {motivo}",
            usuario_registro_id=usuario_id,
            observaciones=f"Ref. Pago original del {pago.fecha_pago}"
        )

        # Helper para obtener sede si no la tienes a mano en el objeto pago
        # (Opcional si tu modelo Pago ya tiene sede_id, si no, úsalo del usuario actual o query extra)
        # Aquí asumo que la pasas o la obtienes. Para el ejemplo, usaremos un placeholder o query.
        # contra_asiento.sede_id = ...
        # CORRECCIÓN RÁPIDA: LibroCaja requiere sede_id.
        # Lo sacaremos del Alumno asociado al pago.
        stmt_alumno = select(Alumno.sede_id).where(Alumno.id == pago.alumno_id)
        sede_id = await self.db.scalar(stmt_alumno)
        contra_asiento.sede_id = sede_id


        self.db.add(contra_asiento)

        return {"mensaje": f"Pago #{pago_id} anulado y deuda restaurada."}
