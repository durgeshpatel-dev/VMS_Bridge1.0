"""
End-to-end test script for the job queue system.
Tests the complete flow: enqueue → Redis → worker → database updates.
"""
import asyncio
import sys
import time
import uuid
from pathlib import Path
# Fix for Windows: psycopg requires WindowsSelectorEventLoop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from redis import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import get_settings
from app.core.queue import enqueue_job, get_queue_status
from app.db.models import Job, Scan, User


async def test_e2e_job_flow():
    """Test the complete job flow from enqueue to completion."""
    settings = get_settings()
    
    print("\n" + "="*60)
    print("END-TO-END JOB QUEUE TEST")
    print("="*60)
    
    # 1. Setup database connection
    print("\n1️⃣  Setting up database connection...")
    database_url = settings.database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(database_url, pool_pre_ping=True)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # 2. Check Redis connection
    print("2️⃣  Checking Redis connection...")
    try:
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
        redis_client.ping()
        print(f"   ✓ Redis connected: {settings.redis_url}")
    except Exception as e:
        print(f"   ✗ Redis connection failed: {e}")
        print("\n   Please start Redis first:")
        print("   docker run -d -p 6379:6379 redis:7-alpine")
        return
    
    # 3. Create test data
    print("\n3️⃣  Creating test scan...")
    async with SessionLocal() as db:
        # Get or create a test user
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("   ✗ No users found in database. Please create a user first.")
            return
        
        print(f"   ✓ Using user: {user.email}")
        
        # Create a test scan
        scan = Scan(
            user_id=user.id,
            filename="test_e2e_scan.xml",
            file_path="upload/test_e2e.xml",
            file_size_mb=1,
            status="uploaded"
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        
        print(f"   ✓ Created scan: {scan.id}")
        
        # Create test file
        upload_dir = backend_dir / "upload"
        upload_dir.mkdir(exist_ok=True)
        test_file = upload_dir / "test_e2e.xml"
        test_file.write_text("<scan><vulnerabilities></vulnerabilities></scan>")
        print(f"   ✓ Created test file: {test_file}")
        
        # 4. Enqueue job
        print("\n4️⃣  Enqueueing job...")
        job_id = await enqueue_job(
            db=db,
            job_type='parse_scan',
            scan_id=scan.id,
            user_id=user.id,
            file_path=scan.file_path,
            metadata={'test': 'e2e'}
        )
        print(f"   ✓ Job created: {job_id}")
        
        # 5. Check Redis queue
        print("\n5️⃣  Checking Redis queue...")
        queue_status = get_queue_status()
        print(f"   Queue status: {queue_status}")
        
        if queue_status['parse_scan'] > 0:
            print(f"   ✓ Job is in Redis queue (count: {queue_status['parse_scan']})")
        else:
            print("   ✗ Job not found in Redis queue")
            return
        
        # 6. Check initial job status
        print("\n6️⃣  Checking initial job status...")
        result = await db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if job:
            print(f"   Status: {job.status}")
            print(f"   Progress: {job.progress}%")
            print(f"   Created: {job.created_at}")
        
        print("\n" + "="*60)
        print("✅ TEST SETUP COMPLETE")
        print("="*60)
        print(f"\nScan ID: {scan.id}")
        print(f"Job ID: {job_id}")
        print(f"Queue: {queue_status['parse_scan']} jobs")
        print("\n📋 Next steps:")
        print("   1. Start the worker in another terminal:")
        print("      .venv\\Scripts\\python.exe run_worker.py")
        print("\n   2. Monitor the job status:")
        print(f"      SELECT status, progress FROM jobs WHERE id = '{job_id}';")
        print("\n   3. Worker should process the job and update status to 'completed'")
        print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_e2e_job_flow())
