"""
Job queue module for async task processing.
Uses Dramatiq + Redis for background job execution.
"""
import uuid
from datetime import datetime
from typing import Any

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from redis import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import Job

settings = get_settings()

# Initialize Redis client
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

# Initialize Dramatiq broker
redis_broker = RedisBroker(url=settings.redis_url)
dramatiq.set_broker(redis_broker)


async def enqueue_job(
    db: AsyncSession,
    job_type: str,
    scan_id: uuid.UUID,
    user_id: uuid.UUID,
    file_path: str,
    metadata: dict[str, Any] | None = None,
) -> uuid.UUID:
    """
    Enqueue a background job for processing.
    
    Creates a Job record in the database with status='pending',
    then pushes the job payload to Redis for worker processing.
    
    Args:
        db: Database session
        job_type: Type of job (e.g., 'parse_scan', 'ml_analysis', 'jira_creation')
        scan_id: ID of the scan to process
        user_id: ID of the user who owns the scan
        file_path: Path to the scan file
        metadata: Optional additional metadata
        
    Returns:
        UUID of the created job
        
    Raises:
        ValueError: If job_type is invalid
    """
    # Validate job_type
    valid_job_types = {'parse_scan', 'ml_analysis', 'jira_creation', 'report_generation'}
    if job_type not in valid_job_types:
        raise ValueError(f"Invalid job_type: {job_type}. Must be one of {valid_job_types}")
    
    # Create idempotency key to prevent duplicate jobs
    idempotency_key = f"scan:{scan_id}:{job_type}"
    
    # Check if a pending/running job already exists for this scan and job type
    result = await db.execute(
        select(Job).where(
            Job.scan_id == scan_id,
            Job.job_type == job_type,
            Job.status.in_(['pending', 'running'])
        )
    )
    existing_job = result.scalar_one_or_none()
    
    if existing_job:
        # Job already exists, return existing job_id
        return existing_job.id
    
    # Create new Job record
    job = Job(
        scan_id=scan_id,
        user_id=user_id,
        job_type=job_type,
        status='pending',
        progress=0,
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Prepare job payload for Redis
    job_payload = {
        'job_id': str(job.id),
        'job_type': job_type,
        'scan_id': str(scan_id),
        'user_id': str(user_id),
        'file_path': file_path,
        'idempotency_key': idempotency_key,
        'created_at': datetime.utcnow().isoformat(),
        'retry_count': 0,
        'meta': metadata or {}
    }
    
    # Push to Redis queue using simple list-based queue
    # Worker will consume from this queue
    queue_name = f"queue:{job_type}"
    redis_client.rpush(queue_name, str(job_payload))
    
    return job.id


def get_queue_status() -> dict[str, Any]:
    """
    Get current queue status for monitoring.
    
    Returns:
        Dictionary with queue lengths for each job type
    """
    job_types = ['parse_scan', 'ml_analysis', 'jira_creation', 'report_generation']
    status = {}
    
    for job_type in job_types:
        queue_name = f"queue:{job_type}"
        length = redis_client.llen(queue_name)
        status[job_type] = length
    
    return status
