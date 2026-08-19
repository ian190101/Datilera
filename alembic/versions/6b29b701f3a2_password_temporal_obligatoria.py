"""Agregar control de contraseña temporal obligatoria.

Revision ID: 6b29b701f3a2
Revises: a14f7c92d601
Create Date: 2026-07-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "6b29b701f3a2"
down_revision: Union[str, None] = "a14f7c92d601"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("debe_cambiar_password", sa.Boolean(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column("usuarios", sa.Column("password_temporal_generada_en", sa.DateTime(), nullable=True))
    op.create_index(
        "ix_usuarios_debe_cambiar_password",
        "usuarios",
        ["debe_cambiar_password"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_usuarios_debe_cambiar_password", table_name="usuarios")
    op.drop_column("usuarios", "password_temporal_generada_en")
    op.drop_column("usuarios", "debe_cambiar_password")
