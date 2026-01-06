"""initial tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # jobs
    op.create_table('jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_type', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_jobs_job_type', 'jobs', ['job_type'], unique=False)

    # jira_projects
    op.create_table('jira_projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('project_key', sa.String(length=32), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=True),
        sa.Column('url', sa.String(length=512), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_key')
    )

    # scans
    op.create_table('scans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('source', sa.String(length=128), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scan_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_scans_status', 'scans', ['status'], unique=False)

    # vulnerabilities
    op.create_table('vulnerabilities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scan_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('severity', sa.String(length=32), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cve', sa.String(length=32), nullable=True),
        sa.Column('package_name', sa.String(length=128), nullable=True),
        sa.Column('installed_version', sa.String(length=64), nullable=True),
        sa.Column('fixed_version', sa.String(length=64), nullable=True),
        sa.Column('raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vulnerabilities_cve'), 'vulnerabilities', ['cve'], unique=False)
    op.create_index(op.f('ix_vulnerabilities_scan_id'), 'vulnerabilities', ['scan_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_vulnerabilities_scan_id'), table_name='vulnerabilities')
    op.drop_index(op.f('ix_vulnerabilities_cve'), table_name='vulnerabilities')
    op.drop_table('vulnerabilities')
    op.drop_index('ix_scans_status', table_name='scans')
    op.drop_table('scans')
    op.drop_table('jira_projects')
    op.drop_index('ix_jobs_job_type', table_name='jobs')
    op.drop_table('jobs')
