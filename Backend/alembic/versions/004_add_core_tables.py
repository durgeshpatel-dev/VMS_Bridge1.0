"""add assets, vulnerabilities, jira_tickets, jobs tables

Revision ID: 004
Revises: 4d6dd79ccfc4
Create Date: 2026-01-09

This migration creates the core security management tables:
- assets: Track servers, APIs, infrastructure targets
- vulnerabilities: Security findings with full lifecycle tracking
- jira_tickets: External ticket tracking (1:1 with vulnerabilities)
- jobs: Background processing for async tasks

Completely replaces the old simple vulnerabilities and jobs tables.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '4d6dd79ccfc4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================
    # 1. DROP OLD TABLES (if they exist)
    # ==========================================
    op.execute("DROP TABLE IF EXISTS jira_projects CASCADE")
    op.execute("DROP TABLE IF EXISTS vulnerabilities CASCADE")
    op.execute("DROP TABLE IF EXISTS jobs CASCADE")
    
    # ==========================================
    # 2. CREATE ASSETS TABLE
    # ==========================================
    op.create_table(
        'assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_identifier', sa.String(length=255), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('asset_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('first_seen', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('last_seen', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.CheckConstraint(
            "asset_type IN ('server', 'api', 'load_balancer', 'application', 'network_device', 'other')",
            name='ck_asset_type'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for assets
    op.create_index('ix_assets_user_id', 'assets', ['user_id'])
    op.create_index('ix_assets_asset_type', 'assets', ['asset_type'])
    op.create_index('ix_assets_last_seen', 'assets', ['last_seen'])
    op.create_index('uq_user_asset', 'assets', ['user_id', 'asset_identifier'], unique=True)
    
    # ==========================================
    # 3. CREATE VULNERABILITIES TABLE
    # ==========================================
    op.create_table(
        'vulnerabilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plugin_id', sa.String(length=100), nullable=True),
        sa.Column('cve_id', sa.String(length=50), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('remediation', sa.Text(), nullable=True),
        sa.Column('scanner_severity', sa.String(length=20), nullable=True),
        sa.Column('cvss_score', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('cvss_vector', sa.String(length=100), nullable=True),
        sa.Column('ml_predicted_risk', sa.String(length=20), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('protocol', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'open'"), nullable=False),
        sa.Column('discovered_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('last_seen', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "scanner_severity IN ('critical', 'high', 'medium', 'low', 'info')",
            name='ck_scanner_severity'
        ),
        sa.CheckConstraint(
            "cvss_score BETWEEN 0.0 AND 10.0",
            name='ck_cvss_score'
        ),
        sa.CheckConstraint(
            "ml_predicted_risk IN ('critical', 'high', 'medium', 'low', 'info')",
            name='ck_ml_predicted_risk'
        ),
        sa.CheckConstraint(
            "risk_score BETWEEN 0 AND 100",
            name='ck_risk_score'
        ),
        sa.CheckConstraint(
            "status IN ('open', 'ignored', 'fixed', 'false_positive')",
            name='ck_status'
        ),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for vulnerabilities
    op.create_index('ix_vulnerabilities_user_id', 'vulnerabilities', ['user_id'])
    op.create_index('ix_vulnerabilities_scan_id', 'vulnerabilities', ['scan_id'])
    op.create_index('ix_vulnerabilities_asset_id', 'vulnerabilities', ['asset_id'])
    op.create_index('ix_vulnerabilities_status', 'vulnerabilities', ['status'])
    op.create_index('ix_vulnerabilities_scanner_severity', 'vulnerabilities', ['scanner_severity'])
    op.create_index('ix_vulnerabilities_cve_id', 'vulnerabilities', ['cve_id'])
    
    # ==========================================
    # 4. CREATE JIRA_TICKETS TABLE
    # ==========================================
    op.create_table(
        'jira_tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vulnerability_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('jira_ticket_key', sa.String(length=50), nullable=False),
        sa.Column('jira_url', sa.Text(), nullable=True),
        sa.Column('jira_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vulnerability_id'], ['vulnerabilities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vulnerability_id'),
        sa.UniqueConstraint('jira_ticket_key')
    )
    
    # Indexes for jira_tickets
    op.create_index('ix_jira_tickets_user_id', 'jira_tickets', ['user_id'])
    op.create_index('ix_jira_tickets_vulnerability_id', 'jira_tickets', ['vulnerability_id'])
    
    # ==========================================
    # 5. CREATE JOBS TABLE
    # ==========================================
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'pending'"), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "job_type IN ('parse_scan', 'ml_analysis', 'jira_creation', 'report_generation')",
            name='ck_job_type'
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled')",
            name='ck_job_status'
        ),
        sa.CheckConstraint(
            "progress BETWEEN 0 AND 100",
            name='ck_progress'
        ),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for jobs
    op.create_index('ix_jobs_scan_id', 'jobs', ['scan_id'])
    op.create_index('ix_jobs_user_id', 'jobs', ['user_id'])
    op.create_index('ix_jobs_status', 'jobs', ['status'])
    op.create_index('ix_jobs_job_type', 'jobs', ['job_type'])


def downgrade() -> None:
    # Drop new tables in reverse order of dependencies
    op.drop_table('jobs')
    op.drop_table('jira_tickets')
    op.drop_table('vulnerabilities')
    op.drop_table('assets')
    
    # Recreate old tables (basic version)
    op.create_table(
        'vulnerabilities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
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
    op.create_index('ix_vulnerabilities_scan_id', 'vulnerabilities', ['scan_id'])
    op.create_index('ix_vulnerabilities_cve', 'vulnerabilities', ['cve'])
    
    op.create_table(
        'jobs',
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
    
    op.create_table(
        'jira_projects',
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
