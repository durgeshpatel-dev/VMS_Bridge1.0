"""Scan upload and management routes."""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.queue import enqueue_job
from app.db.models import Scan, User
from app.db.session import get_db

router = APIRouter(prefix="/scans", tags=["scans"])

# Configure upload directory
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "upload"
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file extensions for security
ALLOWED_EXTENSIONS = {".json", ".xml", ".csv", ".txt", ".sarif", ".cyclonedx"}
MAX_FILE_SIZE_MB = 100


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_scan(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a vulnerability scan file.
    
    Accepts various scan formats (JSON, XML, CSV, SARIF, CycloneDX, etc.)
    Files are stored in the upload directory and a scan record is created in the database.
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Accepted formats: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    
    # Generate unique filename to avoid collisions
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file to disk
    try:
        file_size_bytes = 0
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(8192):  # Read in 8KB chunks
                file_size_bytes += len(chunk)
                
                # Check file size limit
                if file_size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
                    # Delete partial file
                    if file_path.exists():
                        file_path.unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB",
                    )
                
                buffer.write(chunk)
    except Exception as e:
        # Clean up on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}",
        )
    
    # Calculate file size in MB
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    # Create scan record in database
    scan = Scan(
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path.relative_to(UPLOAD_DIR.parent)),
        file_size_mb=int(file_size_mb) if file_size_mb >= 1 else 1,
        status="uploaded",
    )
    
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    
    # Enqueue background job for scan processing
    try:
        job_id = await enqueue_job(
            db=db,
            job_type='parse_scan',
            scan_id=scan.id,
            user_id=current_user.id,
            file_path=str(file_path.relative_to(UPLOAD_DIR.parent)),
            metadata={
                'filename': file.filename,
                'file_size_mb': scan.file_size_mb,
                'source': 'upload_endpoint'
            }
        )
    except Exception as e:
        # Log error but don't fail the upload
        # Scan is already persisted, job can be retried later
        print(f"Warning: Failed to enqueue job for scan {scan.id}: {str(e)}")
        job_id = None
    
    return {
        "id": str(scan.id),
        "filename": scan.filename,
        "file_size_mb": scan.file_size_mb,
        "status": scan.status,
        "uploaded_at": scan.uploaded_at.isoformat(),
        "job_id": str(job_id) if job_id else None,
    }


@router.get("/")
async def list_scans(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all scans for the current user with their latest job status."""
    from sqlalchemy import select, func
    from app.db.models import Job
    
    # Get total count
    count_result = await db.execute(
        select(func.count()).select_from(Scan).where(Scan.user_id == current_user.id)
    )
    total = count_result.scalar()
    
    # Get paginated scans
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(Scan.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
    )
    scans = result.scalars().all()
    
    scans_with_jobs = []
    for scan in scans:
        # Get latest job for this scan
        job_result = await db.execute(
            select(Job)
            .where(Job.scan_id == scan.id)
            .order_by(Job.created_at.desc())
            .limit(1)
        )
        latest_job = job_result.scalar_one_or_none()
        
        scan_data = {
            "id": str(scan.id),
            "filename": scan.filename,
            "file_size_mb": scan.file_size_mb,
            "status": scan.status,
            "uploaded_at": scan.uploaded_at.isoformat(),
            "processed_at": scan.processed_at.isoformat() if scan.processed_at else None,
        }
        
        if latest_job:
            scan_data["job"] = {
                "id": str(latest_job.id),
                "status": latest_job.status,
                "progress": latest_job.progress,
                "job_type": latest_job.job_type,
            }
        else:
            scan_data["job"] = None
        
        scans_with_jobs.append(scan_data)
    
    return {
        "items": scans_with_jobs,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{scan_id}")
async def get_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific scan."""
    from sqlalchemy import select
    
    try:
        scan_uuid = uuid.UUID(scan_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scan ID format",
        )
    
    result = await db.execute(
        select(Scan).where(Scan.id == scan_uuid, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )
    
    return {
        "id": str(scan.id),
        "filename": scan.filename,
        "file_size_mb": scan.file_size_mb,
        "status": scan.status,
        "uploaded_at": scan.uploaded_at.isoformat(),
        "processed_at": scan.processed_at.isoformat() if scan.processed_at else None,
        "metadata": scan.scan_metadata,
    }


@router.get("/{scan_id}/report")
async def get_scan_report(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed scan report with vulnerability statistics and breakdown."""
    from sqlalchemy import select, func
    from app.db.models import Vulnerability, Asset
    
    try:
        scan_uuid = uuid.UUID(scan_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scan ID format",
        )
    
    # Get scan details
    result = await db.execute(
        select(Scan).where(Scan.id == scan_uuid, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )
    
    # Get vulnerability statistics by severity
    severity_counts = {}
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        count = await db.scalar(
            select(func.count()).select_from(Vulnerability).where(
                Vulnerability.user_id == current_user.id,
                Vulnerability.scan_id == scan_uuid,
                Vulnerability.scanner_severity == severity
            )
        )
        severity_counts[severity] = count or 0
    
    # Get total vulnerabilities
    total_vulnerabilities = await db.scalar(
        select(func.count()).select_from(Vulnerability).where(
            Vulnerability.user_id == current_user.id,
            Vulnerability.scan_id == scan_uuid
        )
    )
    
    # Get unique assets affected
    total_assets = await db.scalar(
        select(func.count(func.distinct(Vulnerability.asset_id))).select_from(Vulnerability).where(
            Vulnerability.user_id == current_user.id,
            Vulnerability.scan_id == scan_uuid
        )
    )
    
    # Get vulnerability breakdown by asset type
    asset_type_counts = await db.execute(
        select(
            Asset.asset_type,
            func.count(Vulnerability.id)
        ).join(
            Vulnerability, Asset.id == Vulnerability.asset_id
        ).where(
            Vulnerability.user_id == current_user.id,
            Vulnerability.scan_id == scan_uuid
        ).group_by(Asset.asset_type)
    )
    
    asset_type_breakdown = {row[0]: row[1] for row in asset_type_counts.all()}
    
    # Get top vulnerabilities by severity
    top_vulnerabilities_query = select(Vulnerability, Asset).join(
        Asset, Vulnerability.asset_id == Asset.id
    ).where(
        Vulnerability.user_id == current_user.id,
        Vulnerability.scan_id == scan_uuid
    ).order_by(
        # Order by severity using case statement correctly
        (Vulnerability.scanner_severity == 'critical').desc(),
        (Vulnerability.scanner_severity == 'high').desc(),
        (Vulnerability.scanner_severity == 'medium').desc(),
        (Vulnerability.scanner_severity == 'low').desc(),
        (Vulnerability.scanner_severity == 'info').desc(),
        Vulnerability.cvss_score.desc()
    ).limit(10)
    
    top_vulnerabilities = await db.execute(top_vulnerabilities_query)
    top_vulns = []
    for vuln, asset in top_vulnerabilities.all():
        top_vulns.append({
            "id": str(vuln.id),
            "title": vuln.title,
            "severity": vuln.scanner_severity,
            "cvss_score": float(vuln.cvss_score) if vuln.cvss_score else None,
            "cve_id": vuln.cve_id,
            "asset_identifier": asset.asset_identifier
        })
    
    # Get all vulnerabilities for this scan (paginated)
    vulnerabilities_query = select(Vulnerability, Asset).join(
        Asset, Vulnerability.asset_id == Asset.id
    ).where(
        Vulnerability.user_id == current_user.id,
        Vulnerability.scan_id == scan_uuid
    ).order_by(
        (Vulnerability.scanner_severity == 'critical').desc(),
        (Vulnerability.scanner_severity == 'high').desc(),
        (Vulnerability.scanner_severity == 'medium').desc(),
        (Vulnerability.scanner_severity == 'low').desc(),
        (Vulnerability.scanner_severity == 'info').desc(),
        Vulnerability.cvss_score.desc()
    )
    
    vulnerabilities_result = await db.execute(vulnerabilities_query)
    vulnerabilities = []
    for vuln, asset in vulnerabilities_result.all():
        vulnerabilities.append({
            "id": str(vuln.id),
            "title": vuln.title,
            "severity": vuln.scanner_severity,
            "cvss_score": float(vuln.cvss_score) if vuln.cvss_score else None,
            "cve_id": vuln.cve_id,
            "asset_identifier": asset.asset_identifier,
            "asset_type": asset.asset_type,
            "status": vuln.status,
            "discovered_at": vuln.discovered_at.isoformat()
        })
    
    # Calculate risk score (weighted average based on severity)
    severity_weights = {
        'critical': 5,
        'high': 4,
        'medium': 3,
        'low': 2,
        'info': 1
    }
    
    total_weight = 0
    weighted_sum = 0
    
    for severity, count in severity_counts.items():
        weight = severity_weights.get(severity, 1)
        weighted_sum += count * weight
        total_weight += count
    
    risk_score = int((weighted_sum / (total_weight * 5)) * 100) if total_weight > 0 else 0
    
    return {
        "scan": {
            "id": str(scan.id),
            "filename": scan.filename,
            "file_size_mb": scan.file_size_mb,
            "status": scan.status,
            "uploaded_at": scan.uploaded_at.isoformat(),
            "processed_at": scan.processed_at.isoformat() if scan.processed_at else None,
            "metadata": scan.scan_metadata
        },
        "statistics": {
            "total_vulnerabilities": total_vulnerabilities or 0,
            "total_assets": total_assets or 0,
            "risk_score": risk_score,
            "severity_counts": severity_counts,
            "asset_type_breakdown": asset_type_breakdown
        },
        "top_vulnerabilities": top_vulns,
        "vulnerabilities": vulnerabilities
    }


@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a scan and its associated file."""
    from sqlalchemy import select
    
    try:
        scan_uuid = uuid.UUID(scan_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scan ID format",
        )
    
    result = await db.execute(
        select(Scan).where(Scan.id == scan_uuid, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found",
        )
    
    # Delete file from disk
    file_path = Path(scan.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Error deleting file {file_path}: {e}")
    
    # Delete from database
    await db.delete(scan)
    await db.commit()
    
    return {"message": "Scan deleted successfully"}
