from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

# Modelos
from app.infrastructure.db.models.alumnos.alumnos import Alumno
from app.infrastructure.db.models.finanzas.cuota_plan_pago import CuotaPlanPago
from app.infrastructure.db.models.finanzas.plan_pago_personalizado import PlanPagoPersonalizado
from app.infrastructure.db.models.comunicaciones.notificaciones import Notificacion

class DeudasService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def obtener_lista_morosos(self, sede_id: int) -> list:
        """
        Obtiene todos los alumnos que tienen cuotas vencidas a la fecha de hoy.
        Muestra la deuda real sin recargos inventados.
        """
        hoy = date.today()

        # Consulta: Alumnos con cuotas VENCIDAS (fecha < hoy) y estado NO pagado
        stmt = (
            select(Alumno, CuotaPlanPago, PlanPagoPersonalizado)
            .join(PlanPagoPersonalizado, PlanPagoPersonalizado.alumno_id == Alumno.id)
            .join(CuotaPlanPago, CuotaPlanPago.plan_id == PlanPagoPersonalizado.id)
            .where(
                and_(
                    PlanPagoPersonalizado.sede_id == sede_id,
                    CuotaPlanPago.fecha_vencimiento < hoy,
                    CuotaPlanPago.estado.in_(['pendiente', 'parcial']),
                    PlanPagoPersonalizado.estado == 'activo'
                )
            )
            .order_by(desc(CuotaPlanPago.fecha_vencimiento))
        )

        resultados = await self.db.execute(stmt)
        filas = resultados.all()

        reporte = []
        
        # CORRECCIÓN: Según HU, no hay regla de multa automática definida.
        # Se mantiene en 0 para no alterar los saldos reales.
        MULTA_DIARIA = Decimal(0.00) 

        for alumno, cuota, plan in filas:
            # Calcular deuda real (Lo que costaba la cuota - lo que ya pagó)
            saldo_pendiente = cuota.monto_cuota - cuota.monto_pagado
            
            # Calcular días de atraso (solo informativo)
            dias_atraso = (hoy - cuota.fecha_vencimiento).days
            
            # Recargo en 0
            recargo_mora = dias_atraso * MULTA_DIARIA

            item = {
                "alumno_id": alumno.id,
                "nombre_completo": f"{alumno.apellidos}, {alumno.nombres}",
                "cuota_numero": cuota.numero_cuota,
                "concepto": f"Cuota #{cuota.numero_cuota} (Vencida el {cuota.fecha_vencimiento.strftime('%d/%m')})",
                "fecha_vencimiento": cuota.fecha_vencimiento,
                "dias_atraso": dias_atraso,
                "monto_deuda": float(saldo_pendiente),
                "mora_sugerida": float(recargo_mora), # Será 0.00
                "total_exigible": float(saldo_pendiente + recargo_mora),
                # Nota: Si en el futuro defines una regla (ej: 50 Bs por mes), la cambiamos aquí.
            }
            reporte.append(item)

        return reporte

    async def generar_notificacion_automatica(self, alumno_id: int, cuota_numero: int, usuario_emisor_id: int):
        """
        Genera una notificación interna en el sistema vinculada al Alumno/Padre.
        """
        # 1. Obtener datos básicos
        alumno = await self.db.get(Alumno, alumno_id)
        if not alumno:
            raise ValueError("Alumno no encontrado")
            
        # 2. Determinar destinatario (Tutor)
        # NOTA: Asegúrate de que tu modelo Alumno tenga 'tutor_id' o 'usuario_id'
        # Si no lo tiene, temporalmente usaremos el mismo usuario emisor o null para no romper el código
        usuario_destino_id = getattr(alumno, 'tutor_id', None)
        
        if not usuario_destino_id:
            # Opción B: Si no hay tutor vinculado, no notificamos o notificamos a un admin genérico
            return {"status": "warning", "message": f"El alumno {alumno.nombres} no tiene usuario tutor asociado."}

        mensaje = (
            f"Estimado tutor, le recordamos que la Cuota #{cuota_numero} de {alumno.nombres} "
            f"se encuentra vencida. Por favor pase por administración."
        )

        nueva_notif = Notificacion(
            usuario_id=usuario_destino_id,
            titulo="Recordatorio de Pago",
            mensaje=mensaje,
            tipo="DEUDA",
            leido=False,
            creado_por=usuario_emisor_id
        )
        
        self.db.add(nueva_notif)
        return {"status": "success", "message": "Notificación enviada al tutor."}