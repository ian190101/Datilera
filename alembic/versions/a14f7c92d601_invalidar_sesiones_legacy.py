"""Invalidar sesiones que almacenaban refresh tokens reutilizables.

Revision ID: a14f7c92d601
Revises: 30ccbd5122b9
Create Date: 2026-07-14
"""

from typing import Sequence, Union

from alembic import op


revision: str = "a14f7c92d601"
down_revision: Union[str, None] = "30ccbd5122b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Las filas anteriores contienen tokens completos; se eliminan para que
    # todos los usuarios vuelvan a autenticarse bajo el esquema de huellas.
    op.execute("DELETE FROM sesiones")


def downgrade() -> None:
    # La invalidación de credenciales es deliberadamente irreversible.
    pass
