"""Quick script to check Redis queue status."""
from redis import Redis
from app.core.config import get_settings
from app.core.queue import get_queue_status

settings = get_settings()

try:
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    
    # Test connection
    print(f"✓ Redis connected: {redis_client.ping()}")
    print(f"✓ Redis URL: {settings.redis_url}\n")
    
    # Check queue status
    print("=== QUEUE STATUS ===")
    status = get_queue_status()
    for job_type, count in status.items():
        print(f"  {job_type}: {count} jobs")
    
    print(f"\nTotal jobs in all queues: {sum(status.values())}")
    
except Exception as e:
    print(f"✗ Redis connection failed: {e}")
    print("\nMake sure Redis is running:")
    print("  docker run -d -p 6379:6379 redis:7-alpine")

