"""API routes for vulnerability management."""
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.schemas import VulnerabilityResponse, VulnerabilityListResponse, DashboardStatsResponse
from app.api.routes.auth import get_current_user
from app.db.models import User, Vulnerability, Asset
from app.db.session import get_db

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get vulnerability statistics for the dashboard.
    
    Returns counts by severity level and total assets.
    """
    # Count vulnerabilities by severity
    severity_counts = {}
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        count = await db.scalar(
            select(func.count()).select_from(Vulnerability).where(
                Vulnerability.user_id == current_user.id,
                Vulnerability.scanner_severity == severity,
                Vulnerability.status == 'open'
            )
        )
        severity_counts[severity] = count or 0
    
    # Total vulnerabilities (open only)
    total_vulnerabilities = await db.scalar(
        select(func.count()).select_from(Vulnerability).where(
            Vulnerability.user_id == current_user.id,
            Vulnerability.status == 'open'
        )
    )
    
    # Total assets
    total_assets = await db.scalar(
        select(func.count()).select_from(Asset).where(
            Asset.user_id == current_user.id
        )
    )
    
    return {
        "total_vulnerabilities": total_vulnerabilities or 0,
        "total_assets": total_assets or 0,
        "critical": severity_counts['critical'],
        "high": severity_counts['high'],
        "medium": severity_counts['medium'],
        "low": severity_counts['low'],
        "info": severity_counts['info']
    }


@router.get("", response_model=VulnerabilityListResponse)
async def list_vulnerabilities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    severity: str | None = Query(None, description="Filter by severity (critical, high, medium, low, info)"),
    status: str | None = Query(None, description="Filter by status (open, in_progress, resolved, false_positive)"),
    asset_id: UUID | None = Query(None, description="Filter by asset ID"),
    scan_id: UUID | None = Query(None, description="Filter by scan ID"),
    search: str | None = Query(None, description="Search in title, description, CVE ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
):
    """
    List vulnerabilities with optional filtering.
    
    Supports filtering by:
    - severity: Filter by severity level
    - status: Filter by vulnerability status
    - asset_id: Filter by specific asset
    - scan_id: Filter by specific scan
    - search: Search in title, description, or CVE ID
    """
    # Build query
    query = select(Vulnerability).where(Vulnerability.user_id == current_user.id)
    
    # Apply filters
    if severity:
        query = query.where(Vulnerability.scanner_severity == severity.lower())
    
    if status:
        query = query.where(Vulnerability.status == status.lower())
    
    if asset_id:
        query = query.where(Vulnerability.asset_id == asset_id)
    
    if scan_id:
        query = query.where(Vulnerability.scan_id == scan_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Vulnerability.title.ilike(search_term),
                Vulnerability.description.ilike(search_term),
                Vulnerability.cve_id.ilike(search_term)
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(Vulnerability).where(Vulnerability.user_id == current_user.id)
    
    # Apply same filters to count
    if severity:
        count_query = count_query.where(Vulnerability.scanner_severity == severity.lower())
    if status:
        count_query = count_query.where(Vulnerability.status == status.lower())
    if asset_id:
        count_query = count_query.where(Vulnerability.asset_id == asset_id)
    if scan_id:
        count_query = count_query.where(Vulnerability.scan_id == scan_id)
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(
            or_(
                Vulnerability.title.ilike(search_term),
                Vulnerability.description.ilike(search_term),
                Vulnerability.cve_id.ilike(search_term)
            )
        )
    
    total = await db.scalar(count_query)
    
    # Add eager loading for related data
    query = query.options(joinedload(Vulnerability.asset))
    
    # Order by severity (critical first), then by discovered date
    severity_order = {
        'critical': 0,
        'high': 1,
        'medium': 2,
        'low': 3,
        'info': 4
    }
    query = query.order_by(Vulnerability.discovered_at.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    vulnerabilities = result.unique().scalars().all()
    
    return {
        "items": vulnerabilities,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{vulnerability_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    vulnerability_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single vulnerability by ID."""
    query = select(Vulnerability).where(
        Vulnerability.id == vulnerability_id,
        Vulnerability.user_id == current_user.id
    ).options(joinedload(Vulnerability.asset))
    
    result = await db.execute(query)
    vulnerability = result.unique().scalar_one_or_none()
    
    if not vulnerability:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    return vulnerability
