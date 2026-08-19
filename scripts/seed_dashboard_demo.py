"""Actualiza fechas de datos existentes para una demostración local del dashboard."""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv(dotenv_path=".env")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config.settings import get_settings  # noqa: E402
from app.infrastructure.db.session import AsyncSessionLocal, dispose_engine  # noqa: E402


async def actualizar(*, aplicar: bool) -> None:
    settings = get_settings()
    if settings.is_production:
        raise RuntimeError("Este script de demostración no puede ejecutarse en producción")

    hoy = date.today()
    async with AsyncSessionLocal() as session:
        alumnos = (
            await session.execute(text(
                "SELECT id FROM alumnos WHERE sede_id = 1 AND estado = 'inscrito' "
                "ORDER BY id DESC LIMIT 8"
            ))
        ).scalars().all()
        ingresos = (
            await session.execute(text(
                "SELECT id FROM libro_caja WHERE sede_id = 1 AND tipo = 'INGRESO' "
                "ORDER BY id DESC LIMIT 12"
            ))
        ).scalars().all()
        notificaciones = (
            await session.execute(text(
                "SELECT id FROM notificaciones WHERE usuario_id = 1 ORDER BY id DESC LIMIT 6"
            ))
        ).scalars().all()

        print(
            f"Se prepararán {len(alumnos)} alumnos, {len(ingresos)} ingresos "
            f"y {len(notificaciones)} notificaciones con fechas recientes."
        )
        if not aplicar:
            print("Vista previa: vuelve a ejecutar con --apply para confirmar.")
            return

        async with session.begin_nested():
            for indice, alumno_id in enumerate(alumnos):
                fecha = datetime.combine(hoy - timedelta(days=indice * 3), time(9 + indice % 7, 15))
                await session.execute(
                    text("UPDATE alumnos SET creado_en = :fecha WHERE id = :id"),
                    {"fecha": fecha, "id": alumno_id},
                )

            for indice, movimiento_id in enumerate(ingresos):
                await session.execute(
                    text("UPDATE libro_caja SET fecha = :fecha WHERE id = :id"),
                    {"fecha": hoy - timedelta(days=indice * 2), "id": movimiento_id},
                )

            for indice, notificacion_id in enumerate(notificaciones):
                fecha = datetime.combine(hoy - timedelta(days=indice), time(8 + indice, 30))
                await session.execute(
                    text("UPDATE notificaciones SET creado_en = :fecha WHERE id = :id"),
                    {"fecha": fecha, "id": notificacion_id},
                )

        await session.commit()
        print("Datos de demostración actualizados correctamente.")

    await dispose_engine()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Confirma la actualización de fechas")
    args = parser.parse_args()
    asyncio.run(actualizar(aplicar=args.apply))


if __name__ == "__main__":
    main()
