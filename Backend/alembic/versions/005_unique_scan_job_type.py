"""add unique constraint on scan_id and job_type

Revision ID: 005
Revises: 004
Create Date: 2026-01-09

Prevents duplicate jobs for the same scan and job type.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add unique index on (scan_id, job_type) for pending/running jobs only
    # This prevents duplicate jobs while allowing completed/failed jobs to be retried
    op.create_index(
        'uq_jobs_scan_type_active',
        'jobs',
        ['scan_id', 'job_type'],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'running')")
    )


def downgrade() -> None:
    op.drop_index('uq_jobs_scan_type_active', table_name='jobs')
