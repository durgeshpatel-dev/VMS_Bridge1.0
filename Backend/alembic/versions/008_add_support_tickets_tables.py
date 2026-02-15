"""add support tickets tables

Revision ID: 008_add_support_tickets_tables
Revises: 37dcc15c4a0b
Create Date: 2026-02-15
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_add_support_tickets_tables'
down_revision = '37dcc15c4a0b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'support_tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'open'"), nullable=False),
        sa.Column('priority', sa.String(length=20), server_default=sa.text("'medium'"), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'closed')",
            name='ck_ticket_status'
        ),
        sa.CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'urgent')",
            name='ck_ticket_priority'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_support_tickets_user_id', 'support_tickets', ['user_id'])

    op.create_table(
        'ticket_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['support_tickets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ticket_comments_ticket_id', 'ticket_comments', ['ticket_id'])
    op.create_index('ix_ticket_comments_user_id', 'ticket_comments', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_ticket_comments_user_id', table_name='ticket_comments')
    op.drop_index('ix_ticket_comments_ticket_id', table_name='ticket_comments')
    op.drop_table('ticket_comments')
    op.drop_index('ix_support_tickets_user_id', table_name='support_tickets')
    op.drop_table('support_tickets')
