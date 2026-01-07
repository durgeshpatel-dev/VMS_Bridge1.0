"""add jira_base_url to users

Revision ID: 003
Revises: 002
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('jira_base_url', sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'jira_base_url')
