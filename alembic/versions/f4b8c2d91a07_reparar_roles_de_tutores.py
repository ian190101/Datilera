"""Reparar cuentas de tutores antiguas sin rol de seguridad.

Revision ID: f4b8c2d91a07
Revises: e3a1f7c92026
Create Date: 2026-07-15
"""

from typing import Sequence, Union

from alembic import op


revision: str = "f4b8c2d91a07"
down_revision: Union[str, None] = "e3a1f7c92026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Algunos registros historicos crearon el perfil familiar, pero omitieron
    # la relacion de seguridad. La consulta es idempotente por usuario y rol.
    op.execute(
        """
        INSERT INTO usuarios_roles (usuario_id, rol_id)
        SELECT DISTINCT t.usuario_id, r.id
        FROM tutores AS t
        INNER JOIN roles AS r ON UPPER(r.nombre) = 'TUTOR'
        LEFT JOIN usuarios_roles AS ur
            ON ur.usuario_id = t.usuario_id AND ur.rol_id = r.id
        WHERE t.usuario_id IS NOT NULL
          AND ur.id IS NULL
        """
    )


def downgrade() -> None:
    # Es una reparacion de integridad: retirar el rol volveria a dejar cuentas
    # validas sin acceso y no es posible distinguir asignaciones historicas.
    pass
