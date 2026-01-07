"""recreate_scans_with_uuid_and_file_support

Revision ID: 4d6dd79ccfc4
Revises: 003
Create Date: 2026-01-08 00:31:03.736841

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4d6dd79ccfc4'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing tables completely and recreate with new schema
    # No important data needs to be preserved (confirmed by user)
    
    # Drop vulnerabilities first (has FK to scans)
    op.drop_table('vulnerabilities')
    
    # Drop scans table
    op.drop_table('scans')
    
    # Recreate scans table with UUID and file upload support
    op.create_table(
        'scans',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('file_size_mb', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'uploaded'"), nullable=False),
        sa.Column('scan_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scans_user_id'), 'scans', ['user_id'], unique=False)
    op.create_index(op.f('ix_scans_status'), 'scans', ['status'], unique=False)
    
    # Recreate vulnerabilities table with UUID scan_id
    op.create_table(
        'vulnerabilities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scan_id', sa.UUID(), nullable=False),
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
    
    # Fix users table email index (make unique)
    op.drop_constraint('users_email_key', 'users', type_='unique')
    op.drop_index('ix_users_email', table_name='users')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # Restore original scans and vulnerabilities tables
    
    # Drop new tables
    op.drop_index(op.f('ix_vulnerabilities_scan_id'), table_name='vulnerabilities')
    op.drop_index(op.f('ix_vulnerabilities_cve'), table_name='vulnerabilities')
    op.drop_table('vulnerabilities')
    
    op.drop_index(op.f('ix_scans_status'), table_name='scans')
    op.drop_index(op.f('ix_scans_user_id'), table_name='scans')
    op.drop_table('scans')
    
    # Recreate original scans table
    op.create_table(
        'scans',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('status', sa.VARCHAR(length=32), nullable=False),
        sa.Column('scan_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.VARCHAR(length=128), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('started_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('finished_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate original vulnerabilities table
    op.create_table(
        'vulnerabilities',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('scan_id', sa.INTEGER(), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('severity', sa.String(length=32), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cve', sa.String(length=32), nullable=True),
        sa.Column('package_name', sa.String(length=128), nullable=True),
        sa.Column('installed_version', sa.String(length=64), nullable=True),
        sa.Column('fixed_version', sa.String(length=64), nullable=True),
        sa.Column('raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vulnerabilities_cve', 'vulnerabilities', ['cve'], unique=False)
    
    # Restore users table email index
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.create_unique_constraint('users_email_key', 'users', ['email'])
    # ### end Alembic commands ###
