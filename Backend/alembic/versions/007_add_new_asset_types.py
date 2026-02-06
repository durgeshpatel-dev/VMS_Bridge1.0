"""Add new asset types for dependency, code, and container scanning."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_new_asset_types'
down_revision = '4d6dd79ccfc4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add dependency, code, and container asset types."""
    # Drop the existing constraint
    op.drop_constraint('ck_asset_type', 'assets')
    
    # Create new constraint with additional asset types
    op.create_check_constraint(
        'ck_asset_type',
        'assets',
        "asset_type IN ('server', 'api', 'load_balancer', 'application', 'network_device', 'dependency', 'container', 'code', 'other')"
    )


def downgrade() -> None:
    """Remove the new asset types."""
    # Drop the updated constraint
    op.drop_constraint('ck_asset_type', 'assets')
    
    # Restore the original constraint
    op.create_check_constraint(
        'ck_asset_type',
        'assets',
        "asset_type IN ('server', 'api', 'load_balancer', 'application', 'network_device', 'other')"
    )
