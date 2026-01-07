"""Verify database schema after migration."""
from sqlalchemy import create_engine, inspect
from app.core.config import get_settings

# Use sync engine for inspection
settings = get_settings()
sync_url = settings.database_url.replace('postgresql+asyncpg', 'postgresql')
engine = create_engine(sync_url)
inspector = inspect(engine)

print('Scans table columns:')
scans_cols = inspector.get_columns('scans')
for col in scans_cols:
    nullable = 'NULL' if col['nullable'] else 'NOT NULL'
    print(f"  {col['name']}: {col['type']} {nullable}")

print('\nVulnerabilities table columns:')
vuln_cols = inspector.get_columns('vulnerabilities')
for col in vuln_cols:
    nullable = 'NULL' if col['nullable'] else 'NOT NULL'
    print(f"  {col['name']}: {col['type']} {nullable}")

print('\nScans table indexes:')
scans_indexes = inspector.get_indexes('scans')
for idx in scans_indexes:
    print(f"  {idx['name']}: {idx['column_names']}")

print('\nScans table foreign keys:')
scans_fks = inspector.get_foreign_keys('scans')
for fk in scans_fks:
    print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

