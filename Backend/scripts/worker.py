"""
Background worker for processing scan jobs.
Consumes jobs from Redis queues and updates job status in the database.
"""
import asyncio
import json
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

# Fix for Windows: psycopg requires WindowsSelectorEventLoop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from redis import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import get_settings
from app.core.parsers import get_parser
from app.core.parsers.base import ParseResult
from app.db.models import Asset, Job, Scan, Vulnerability


settings = get_settings()

# Create async engine for worker
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

async_engine = create_async_engine(database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Redis client
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def get_db_session() -> AsyncSession:
    """Create a new database session."""
    return AsyncSessionLocal()


async def update_job_status(
    db: AsyncSession,
    job_id: uuid.UUID,
    status: str,
    progress: int | None = None,
    error_message: str | None = None,
    result_data: dict | None = None,
):
    """Update job status in the database."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        print(f"Warning: Job {job_id} not found in database")
        return
    
    job.status = status
    
    if progress is not None:
        job.progress = progress
    
    if error_message:
        job.error_message = error_message
    
    if result_data:
        job.result_data = result_data
    
    if status == 'running' and not job.started_at:
        job.started_at = datetime.utcnow()
    
    if status in ('completed', 'failed', 'cancelled'):
        job.completed_at = datetime.utcnow()
    
    await db.commit()
    print(f"✓ Job {job_id} status updated: {status} (progress: {progress}%)")


async def process_scan_file(
    file_path: str, 
    job_id: uuid.UUID, 
    scan_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession
) -> dict:
    """
    Process a scan file and extract vulnerability data.
    
    Parses the scan file, creates assets and vulnerabilities in the database.
    """
    print(f"  Processing file: {file_path}")
    
    # Resolve file path relative to Backend directory
    backend_dir = Path(__file__).parent.parent
    full_path = backend_dir / file_path
    
    print(f"  Looking for file at: {full_path}")
    
    if not full_path.exists():
        raise FileNotFoundError(f"Scan file not found: {full_path}")
    
    # Step 1: Parse the scan file
    await update_job_status(db, job_id, 'running', progress=10)
    print(f"  Parsing scan file...")
    
    try:
        parser = get_parser(str(full_path))
        parse_result: ParseResult = parser.parse(str(full_path))
    except Exception as e:
        raise ValueError(f"Failed to parse scan file: {e}")
    
    print(f"  Found {len(parse_result.vulnerabilities)} vulnerabilities")
    print(f"  Found {len(parse_result.assets)} assets")
    
    # Step 2: Create or update assets
    await update_job_status(db, job_id, 'running', progress=30)
    print(f"  Creating assets...")
    
    asset_map = {}  # Map asset_identifier to Asset.id
    for parsed_asset in parse_result.assets:
        # Check if asset already exists for this user
        result = await db.execute(
            select(Asset).where(
                Asset.user_id == user_id,
                Asset.asset_identifier == parsed_asset.asset_identifier
            )
        )
        asset = result.scalar_one_or_none()
        
        if asset:
            # Update last_seen
            asset.last_seen = datetime.utcnow()
            if parsed_asset.metadata:
                asset.asset_metadata = parsed_asset.metadata
        else:
            # Create new asset
            asset = Asset(
                user_id=user_id,
                asset_identifier=parsed_asset.asset_identifier,
                asset_type=parsed_asset.asset_type,
                asset_metadata=parsed_asset.metadata
            )
            db.add(asset)
        
        await db.flush()  # Get asset ID
        asset_map[parsed_asset.asset_identifier] = asset.id
    
    await db.commit()
    print(f"  Created/updated {len(asset_map)} assets")
    
    # Step 3: Create or update vulnerabilities (deduplication)
    await update_job_status(db, job_id, 'running', progress=50)
    print(f"  Creating/updating vulnerabilities with deduplication...")
    
    vulnerabilities_created = 0
    vulnerabilities_updated = 0
    batch_size = 100
    
    for i, parsed_vuln in enumerate(parse_result.vulnerabilities):
        # Get asset ID
        asset_id = asset_map.get(parsed_vuln.asset_identifier)
        if not asset_id:
            print(f"  Warning: Asset not found for {parsed_vuln.asset_identifier}, skipping vulnerability")
            continue
        
        # Check if vulnerability already exists (deduplication)
        # A vulnerability is considered duplicate if it has the same:
        # - asset_id (same host/target)
        # - plugin_id OR cve_id (same vulnerability type)
        # - port (same service/location)
        existing_query = select(Vulnerability).where(
            Vulnerability.user_id == user_id,
            Vulnerability.asset_id == asset_id,
            Vulnerability.port == parsed_vuln.port
        )
        
        # Match by plugin_id or cve_id (whichever is available)
        if parsed_vuln.plugin_id:
            existing_query = existing_query.where(Vulnerability.plugin_id == parsed_vuln.plugin_id)
        elif parsed_vuln.cve_id:
            existing_query = existing_query.where(Vulnerability.cve_id == parsed_vuln.cve_id)
        else:
            # If no plugin_id or cve_id, match by title (less reliable but better than duplicates)
            existing_query = existing_query.where(Vulnerability.title == parsed_vuln.title)
        
        result = await db.execute(existing_query)
        existing_vuln = result.scalar_one_or_none()
        
        if existing_vuln:
            # Update existing vulnerability
            existing_vuln.last_seen = datetime.utcnow()
            existing_vuln.scan_id = scan_id  # Update to latest scan
            
            # If vulnerability was closed but found again, reopen it
            if existing_vuln.status in ['resolved', 'false_positive']:
                existing_vuln.status = 'open'
                existing_vuln.closed_at = None
                print(f"  Reopened vulnerability: {existing_vuln.title}")
            
            # Update details if they changed (e.g., new description, remediation)
            if parsed_vuln.description:
                existing_vuln.description = parsed_vuln.description
            if parsed_vuln.remediation:
                existing_vuln.remediation = parsed_vuln.remediation
            if parsed_vuln.cvss_score:
                existing_vuln.cvss_score = parsed_vuln.cvss_score
            if parsed_vuln.cvss_vector:
                existing_vuln.cvss_vector = parsed_vuln.cvss_vector
            
            vulnerabilities_updated += 1
        else:
            # Create new vulnerability
            vuln = Vulnerability(
                user_id=user_id,
                scan_id=scan_id,
                asset_id=asset_id,
                plugin_id=parsed_vuln.plugin_id,
                cve_id=parsed_vuln.cve_id,
                title=parsed_vuln.title,
                description=parsed_vuln.description,
                remediation=parsed_vuln.remediation,
                scanner_severity=parsed_vuln.scanner_severity,
                cvss_score=parsed_vuln.cvss_score,
                cvss_vector=parsed_vuln.cvss_vector,
                port=parsed_vuln.port,
                protocol=parsed_vuln.protocol,
                status='open'
            )
            db.add(vuln)
            vulnerabilities_created += 1
        
        # Commit in batches and update progress
        if (i + 1) % batch_size == 0:
            await db.commit()
            progress = 50 + int((i + 1) / len(parse_result.vulnerabilities) * 40)
            await update_job_status(db, job_id, 'running', progress=progress)
            print(f"  Processed {i + 1}/{len(parse_result.vulnerabilities)} vulnerabilities...")
    
    # Final commit
    await db.commit()
    print(f"  Created {vulnerabilities_created} new vulnerabilities, updated {vulnerabilities_updated} existing ones")
    
    # Step 4: Finalize
    await update_job_status(db, job_id, 'running', progress=100)
    
    # Get file size
    file_size = full_path.stat().st_size
    
    result = {
        'file_path': file_path,
        'file_size_bytes': file_size,
        'vulnerabilities_found': vulnerabilities_created,
        'assets_found': len(asset_map),
        'parser': parse_result.metadata.get('parser', 'unknown'),
        'processed_at': datetime.utcnow().isoformat(),
        'status': 'success'
    }
    
    return result


async def parse_scan(job_payload: dict):
    """
    Main worker function to process a scan job.
    
    Args:
        job_payload: Dictionary containing job details from Redis
    """
    job_id = uuid.UUID(job_payload['job_id'])
    scan_id = uuid.UUID(job_payload['scan_id'])
    user_id = uuid.UUID(job_payload['user_id'])
    file_path = job_payload['file_path']
    
    print(f"\n{'='*60}")
    print(f"🔄 Processing job: {job_id}")
    print(f"   Scan ID: {scan_id}")
    print(f"   File: {file_path}")
    print(f"{'='*60}")
    
    async with await get_db_session() as db:
        try:
            # Mark job as running
            await update_job_status(db, job_id, 'running', progress=0)
            
            # Process the scan file
            result = await process_scan_file(file_path, job_id, scan_id, user_id, db)
            
            # Mark job as completed
            await update_job_status(
                db,
                job_id,
                'completed',
                progress=100,
                result_data=result
            )
            
            # Update scan's processed_at timestamp
            scan_result = await db.execute(select(Scan).where(Scan.id == scan_id))
            scan = scan_result.scalar_one_or_none()
            if scan:
                scan.processed_at = datetime.utcnow()
                scan.status = 'processed'
                await db.commit()
                print(f"✓ Scan {scan_id} marked as processed")
            
            print(f"✅ Job {job_id} completed successfully\n")
            
        except Exception as e:
            # Mark job as failed
            error_msg = f"{type(e).__name__}: {str(e)}"
            await update_job_status(
                db,
                job_id,
                'failed',
                error_message=error_msg
            )
            print(f"❌ Job {job_id} failed: {error_msg}\n")
            raise


async def worker_loop(queue_name: str = "queue:parse_scan"):
    """
    Main worker loop that consumes jobs from Redis.
    
    Args:
        queue_name: Name of the Redis queue to consume from
    """
    print(f"🚀 Worker started - listening on {queue_name}")
    print(f"   Redis: {settings.redis_url}")
    print(f"   Database: {settings.database_url[:50]}...")
    print(f"\nWaiting for jobs...\n")
    
    while True:
        try:
            # Blocking pop from Redis queue (timeout 1 second)
            result = redis_client.blpop(queue_name, timeout=1)
            
            if result:
                _, job_payload_str = result
                job_payload = eval(job_payload_str)  # Convert string back to dict
                
                # Process the job
                await parse_scan(job_payload)
            else:
                # No job available, sleep briefly
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n⚠️  Worker stopped by user")
            break
        except Exception as e:
            print(f"❌ Worker error: {e}")
            await asyncio.sleep(1)  # Prevent tight error loop


def main():
    """Entry point for the worker."""
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        print("\n✓ Worker shutdown complete")


if __name__ == "__main__":
    main()
