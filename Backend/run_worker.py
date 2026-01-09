"""
Run the background worker process.
Starts the worker that processes scan jobs from Redis.
"""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from scripts.worker import main

if __name__ == "__main__":
    print("="*60)
    print("VMC Bridge - Background Worker")
    print("="*60)
    print("\nStarting worker process...")
    print("Press Ctrl+C to stop\n")
    
    main()
