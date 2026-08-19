"""Agregar trazabilidad de pagos aplicados a cuotas.

Revision ID: c7d9e41a8b02
Revises: 6b29b701f3a2
Create Date: 2026-07-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c7d9e41a8b02"
down_revision: Union[str, None] = "6b29b701f3a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pagos_cuotas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pago_id", sa.Integer(), nullable=False),
        sa.Column("cuota_id", sa.Integer(), nullable=False),
        sa.Column("monto_aplicado", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("creado_en", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cuota_id"], ["cuotas_plan_pago.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["pago_id"], ["pagos.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pago_id", "cuota_id", name="uq_pago_cuota"),
    )
    op.create_index("ix_pagos_cuotas_pago", "pagos_cuotas", ["pago_id"], unique=False)
    op.create_index("ix_pagos_cuotas_cuota", "pagos_cuotas", ["cuota_id"], unique=False)

    # Conserva la relación histórica disponible antes de introducir la tabla puente.
    op.execute(
        """
        INSERT INTO pagos_cuotas (pago_id, cuota_id, monto_aplicado)
        SELECT pago_id, id, LEAST(monto_pagado, monto_cuota + mora)
        FROM cuotas_plan_pago
        WHERE pago_id IS NOT NULL AND monto_pagado > 0
        """
    )


def downgrade() -> None:
    op.drop_index("ix_pagos_cuotas_cuota", table_name="pagos_cuotas")
    op.drop_index("ix_pagos_cuotas_pago", table_name="pagos_cuotas")
    op.drop_table("pagos_cuotas")
