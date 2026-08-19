"""Agregar horarios y archivado individual de conversaciones.

Revision ID: e3a1f7c92026
Revises: c7d9e41a8b02
Create Date: 2026-07-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "e3a1f7c92026"
down_revision: Union[str, None] = "c7d9e41a8b02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversaciones_participantes",
        sa.Column("archivado", sa.Boolean(), server_default=sa.text("0"), nullable=False),
    )
    op.create_index(
        "ix_conversaciones_participantes_archivado",
        "conversaciones_participantes",
        ["archivado"],
        unique=False,
    )
    op.create_table(
        "horarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=50), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fin", sa.Time(), nullable=False),
        sa.Column("creado_en", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )
    op.create_index("ix_horarios_nombre", "horarios", ["nombre"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_horarios_nombre", table_name="horarios")
    op.drop_table("horarios")
    op.drop_index("ix_conversaciones_participantes_archivado", table_name="conversaciones_participantes")
    op.drop_column("conversaciones_participantes", "archivado")
