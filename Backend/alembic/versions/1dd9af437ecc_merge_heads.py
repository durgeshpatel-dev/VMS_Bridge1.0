"""merge_heads

Revision ID: 1dd9af437ecc
Revises: 006, 007_add_new_asset_types
Create Date: 2026-02-15 18:01:32.818474

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '1dd9af437ecc'
down_revision = ('006', '007_add_new_asset_types')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
