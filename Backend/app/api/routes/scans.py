"""Scan upload and management routes."""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
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
    
    return {
        "id": str(scan.id),
        "filename": scan.filename,
        "file_size_mb": scan.file_size_mb,
        "status": scan.status,
        "uploaded_at": scan.uploaded_at.isoformat(),
    }


@router.get("/")
async def list_scans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all scans for the current user."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(Scan.uploaded_at.desc())
    )
    scans = result.scalars().all()
    
    return [
        {
            "id": str(scan.id),
            "filename": scan.filename,
            "file_size_mb": scan.file_size_mb,
            "status": scan.status,
            "uploaded_at": scan.uploaded_at.isoformat(),
            "processed_at": scan.processed_at.isoformat() if scan.processed_at else None,
        }
        for scan in scans
    ]


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
