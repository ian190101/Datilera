# app/infrastructure/tasks/reportestasks.py
from __future__ import annotations

import asyncio
import csv
from decimal import Decimal
from io import StringIO
from typing import Any, Iterable, Mapping, List, Optional, cast, Dict

# 1. Imports de Base de Datos y Sesión
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_session

# 2. Imports de Modelos
from app.infrastructure.db.models.finanzas import Arqueo, LibroCaja
from app.infrastructure.db.models.exportacion.exportacion import (
    Exportacion, 
    EstadoExportacion,
    TipoReporte,
    FormatoArchivo
)

# 3. Imports de Repositorios
from app.infrastructure.db.repositories.finanzas.arqueos_repo import ArqueosRepository
from app.infrastructure.db.repositories.finanzas.libro_caja_repo import LibroCajaRepository
from app.infrastructure.db.repositories.exportacion.exportacion_repo import ExportacionRepository

# 4. Imports de Storage
from app.infrastructure.storage.local_fs import LocalFileStorage
from app.infrastructure.storage.export_excel import ExcelExportStorage
from app.infrastructure.storage.pdfs import PDFReportStorage


# ==============================================================================
# TAREA 1: REPORTE DE ARQUEO MENSUAL
# ==============================================================================

def generar_reporte_arqueo_mensual(sede_id: int, anio: int, mes: int) -> None:
    """Entrypoint síncrono para workers (RQ/Celery)."""
    asyncio.run(_generar_arqueo_async(sede_id, anio, mes))


async def _generar_arqueo_async(sede_id: int, anio: int, mes: int) -> None:
    session: AsyncSession
    async with get_session() as session:
        arqueos_repo = ArqueosRepository(session)
        
        pdf_storage = PDFReportStorage()
        excel_storage = ExcelExportStorage()

        # 1. Obtener los datos calculados usando el método de tu repositorio
        # Esto devuelve un dict con: saldo_inicial, total_ingresos, total_egresos, saldo_final y movimientos
        datos_financieros: Dict[str, Any] = await arqueos_repo.obtener_datos_arqueo(
            sede_id=sede_id,
            mes=mes,
            año=anio
        )

        movimientos: List[LibroCaja] = datos_financieros['movimientos']

        # 2. Convertir entidades LibroCaja a Dicts para los generadores de PDF/Excel
        datos_para_reporte = []
        for mov in movimientos:
            datos_para_reporte.append({
                "fecha": mov.fecha,
                "concepto": mov.concepto,
                "ingreso": mov.monto if getattr(mov, "tipo_movimiento", "") == 'ingreso' or getattr(mov, "tipo", "") == 'ingreso' else 0,
                "egreso": mov.monto if getattr(mov, "tipo_movimiento", "") == 'egreso' or getattr(mov, "tipo", "") == 'egreso' else 0,
                "saldo": mov.saldo_acumulado,
                "referencia": mov.referencia or "",
                "observaciones": getattr(mov, "observaciones", "")
            })

        # 3. Generar archivos físicos (I/O)
        pdf_path = pdf_storage.generar_arqueo_mensual_pdf(
            sede_id=sede_id,
            anio=anio,
            mes=mes,
            datos=datos_para_reporte,
            resumen={
                "saldo_inicial": datos_financieros["saldo_inicial"],
                "ingresos": datos_financieros["total_ingresos"],
                "egresos": datos_financieros["total_egresos"],
                "saldo_final": datos_financieros["saldo_final"]
            }
        )

        excel_path = excel_storage.generar_arqueo_mensual_excel(
            sede_id=sede_id,
            anio=anio,
            mes=mes,
            datos=datos_para_reporte,
        )

        # 4. Lógica "Upsert" (Crear o Actualizar) manual
        # Como no tienes registrar_o_actualizar, lo hacemos aquí:
        
        arqueo_existente = await arqueos_repo.obtener_por_mes_anio(sede_id, mes, anio)

        if arqueo_existente:
            # ACTUALIZAR
            await arqueos_repo.actualizar_arqueo(
                arqueo_id=arqueo_existente.id,
                saldo_inicial=Decimal(str(datos_financieros["saldo_inicial"])),
                total_ingresos=Decimal(str(datos_financieros["total_ingresos"])),
                total_egresos=Decimal(str(datos_financieros["total_egresos"])),
                pdf_url=pdf_path
                # Si tu modelo tiene excel_url, agrégalo al método actualizar_arqueo en el repo
            )
        else:
            # CREAR
            # Nota: Necesitas un ID de usuario sistema o admin para "elaborado_por_id"
            # Aquí pongo 1 por defecto, o podrías pasarlo como argumento a la tarea
            USUARIO_SISTEMA_ID = 1 
            
            await arqueos_repo.crear_arqueo_mensual(
                sede_id=sede_id,
                mes=mes,
                anio=anio,
                saldo_inicial=Decimal(str(datos_financieros["saldo_inicial"])),
                total_ingresos=Decimal(str(datos_financieros["total_ingresos"])),
                total_egresos=Decimal(str(datos_financieros["total_egresos"])),
                elaborado_por_id=USUARIO_SISTEMA_ID,
                observaciones=f"Generado automáticamente. PDF: {pdf_path}"
            )

        await session.commit()


# ==============================================================================
# TAREA 2: EXPORTACIÓN MASIVA
# ==============================================================================

def generar_exportacion_masiva(exportacion_id: int) -> None:
    """Entrypoint síncrono."""
    asyncio.run(_generar_exportacion_async(exportacion_id))


async def _generar_exportacion_async(exportacion_id: int) -> None:
    session: AsyncSession
    async with get_session() as session:
        export_repo = ExportacionRepository(session)
        storage = LocalFileStorage()
        excel_storage = ExcelExportStorage()

        exportacion = await export_repo.obtener_por_id(exportacion_id)
        
        if not exportacion:
            return

        # Mapeo de campos
        filtros = exportacion.filtros or {}
        tipo_reporte = exportacion.tipo_reporte
        formato_enum = cast(FormatoArchivo, exportacion.formato)
        formato_str = formato_enum.value

        try:
            # Obtener datos (Simulación - Aquí conectarías tus otros Repos)
            filas = await _obtener_datos_para_reporte(session, tipo_reporte, filtros)
            
            ruta = ""
            if formato_str == "xlsx":
                ruta = excel_storage.generar_exportacion_excel(
                    exportacion_id=exportacion_id, 
                    datos=filas, 
                    config=filtros
                )
            else:
                csv_bytes = _serializar_csv(filas)
                nombre_archivo = f"export_{exportacion_id}.csv"
                ruta = storage.save_bytes(
                    f"exportaciones/{nombre_archivo}",
                    csv_bytes,
                    overwrite=True,
                )

            # Actualizar estado a COMPLETADO
            await export_repo.actualizar_estado(
                exportacion_id=exportacion_id,
                estado=EstadoExportacion.COMPLETADO,
                ruta_archivo=ruta,
                tamano_bytes=1024  # Calcular real si es posible
            )

        except Exception as e:
            # Actualizar estado a ERROR
            await export_repo.actualizar_estado(
                exportacion_id=exportacion_id,
                estado=EstadoExportacion.ERROR,
                error_mensaje=str(e)
            )

        await session.commit()


# ==============================================================================
# HELPERS
# ==============================================================================

async def _obtener_datos_para_reporte(
    session: AsyncSession, 
    tipo: TipoReporte, 
    filtros: dict
) -> List[dict]:
    """
    Switch para obtener datos según el tipo de reporte.
    """
    # Aquí debes importar e instanciar los repositorios según el tipo
    # if tipo == TipoReporte.ALUMNOS:
    #     return await AlumnosRepository(session).listar_con_filtros(filtros)
    
    return [{"mensaje": "Datos de prueba", "tipo": str(tipo)}]


def _serializar_csv(
    filas: Iterable[Mapping[str, Any]],
    headers: Optional[List[str]] = None,
) -> bytes:
    filas_lista = list(filas)
    if not filas_lista:
        return "Mensaje\nSin datos para exportar\n".encode("utf-8")

    if not headers:
        headers = list(filas_lista[0].keys())

    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=headers)
    writer.writeheader()
    for fila in filas_lista:
        clean_row = {k: fila.get(k, "") for k in headers}
        writer.writerow(clean_row)

    return buf.getvalue().encode("utf-8")
