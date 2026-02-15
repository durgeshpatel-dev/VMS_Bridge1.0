"""add_is_admin_column

Revision ID: 37dcc15c4a0b
Revises: 1dd9af437ecc
Create Date: 2026-02-15 18:01:39.672693

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '37dcc15c4a0b'
down_revision = '1dd9af437ecc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False))


def downgrade() -> None:
    # Remove is_admin column from users table
    op.drop_column('users', 'is_admin')
