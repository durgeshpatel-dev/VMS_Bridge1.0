import sys
import os

# Add the parent directory to sys.path so we can import 'app'
# This assumes the script is run from the backend root or backend/scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(current_dir)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from sqlalchemy import select
from app.db.session import init_engine_and_sessionmaker, get_engine
from app.db.models import Scan, Vulnerability, Job, JiraProject
from sqlalchemy.orm import Session

def main():
    print("--- Manual DB Test ---")
    
    # 1. Initialize DB
    try:
        init_engine_and_sessionmaker()
        engine = get_engine()
        # Ensure we can connect
        with engine.connect() as conn:
            print("Connected to database successfully.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        print("Did you set DATABASE_URL in .env and is the DB running?")
        print("Tip: Ensure you have run 'alembic upgrade head' to create tables.")
        sys.exit(1)

    # 2. Use a session
    with Session(engine) as session:
        print("\n--- Inserting Data ---")
        
        # Create a Scan
        scan = Scan(
            status="completed",
            source="manual_test",
            scan_metadata={"test_run": True}
        )
        session.add(scan)
        session.flush() # get ID
        print(f"Inserted Scan ID: {scan.id}")

        # Create a Vulnerability
        vuln = Vulnerability(
            scan_id=scan.id,
            title="Test Vulnerability",
            severity="High",
            description="This is a test vulnerability inserted manually.",
            cve="CVE-2099-12345",
            package_name="test-package"
        )
        session.add(vuln)
        
        # Create a Job
        job = Job(
            job_type="scan_sync",
            status="queued",
            payload={"scan_id": scan.id}
        )
        session.add(job)
        
        # Create a Jira Project
        # Use a unique key
        import uuid
        project_key = f"TEST-{uuid.uuid4().hex[:4].upper()}"
        jp = JiraProject(
            project_key=project_key,
            name="Test Project",
            url="https://jira.example.com/projects/TEST"
        )
        session.add(jp)
        
        session.commit()
        print("Committed Scan, Vulnerability, Job, and JiraProject.")

        print("\n--- Querying Data ---")
        
        # Query Scan
        scan_db = session.get(Scan, scan.id)
        if scan_db:
            print(f"Found Scan: ID={scan_db.id}, Status={scan_db.status}, Vuln Count={len(scan_db.vulnerabilities)}")
        
        # Query Vuln
        stmt_vuln = select(Vulnerability).where(Vulnerability.cve == "CVE-2099-12345")
        vulns = session.scalars(stmt_vuln).all()
        for v in vulns:
            print(f"Found Vuln: {v.title} (Scan ID: {v.scan_id})")

        # Query Job
        stmt_job = select(Job).limit(1)
        job_db = session.scalars(stmt_job).first()
        if job_db:
             print(f"Found Job: {job_db.job_type} (Status: {job_db.status})")
             
        # Query Jira Project
        stmt_jp = select(JiraProject).where(JiraProject.project_key == project_key)
        jp_db = session.scalars(stmt_jp).first()
        if jp_db:
            print(f"Found Jira Project: {jp_db.project_key} - {jp_db.name}")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    main()
