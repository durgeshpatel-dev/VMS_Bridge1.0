"""API routes for admin panel management."""
from typing import List
from uuid import UUID
from datetime import datetime
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    UserListResponse,
    UserResponse,
    UserStatsResponse,
    AdminActivityResponse,
    AdminSystemInfoResponse,
    UpdateUserRoleRequest,
    SupportTicketListResponse,
    SupportTicketResponse,
    UpdateTicketStatusRequest,
    UpdateTicketPriorityRequest,
    CreateTicketCommentRequest,
    TicketCommentResponse,
    MessageResponse,
)
from app.api.routes.auth import get_current_user
from app.core.config import get_settings
from app.db.models import User, SupportTicket, TicketComment
from app.db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])
settings = get_settings()
APP_START_TIME = datetime.utcnow()


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated admin user."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access admin panel")
    return current_user


@router.get("/stats", response_model=UserStatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get admin dashboard statistics."""
    # Get user stats
    total_users = await db.scalar(select(func.count(User.id)))
    active_users = await db.scalar(select(func.count(User.id)).where(User.is_active))
    admin_users = await db.scalar(select(func.count(User.id)).where(User.is_admin))
    
    # Get ticket stats
    total_tickets = await db.scalar(select(func.count(SupportTicket.id)))
    open_tickets = await db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status == "open"))
    in_progress_tickets = await db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status == "in_progress"))
    resolved_tickets = await db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status == "resolved"))
    closed_tickets = await db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status == "closed"))
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
    }


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List all users (admin only)."""
    query = select(User).offset(skip).limit(limit)
    results = await db.execute(query)
    users = results.scalars().all()
    
    total = await db.scalar(select(func.count(User.id)))
    
    return {
        "items": users,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get user details (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    request: UpdateUserRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update user role (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = request.is_admin
    await db.commit()
    await db.refresh(user)
    
    return user


@router.patch("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: UUID,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update user active status (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    
    return user


@router.get("/tickets", response_model=SupportTicketListResponse)
async def list_support_tickets(
    skip: int = 0,
    limit: int = 50,
    status: str | None = None,
    priority: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List all support tickets (admin only)."""
    query = select(SupportTicket)
    
    if status:
        query = query.where(SupportTicket.status == status)
    if priority:
        query = query.where(SupportTicket.priority == priority)
    
    query = query.offset(skip).limit(limit)
    results = await db.execute(query)
    tickets = results.scalars().all()
    
    count_query = select(func.count(SupportTicket.id))
    if status:
        count_query = count_query.where(SupportTicket.status == status)
    if priority:
        count_query = count_query.where(SupportTicket.priority == priority)
    total = await db.scalar(count_query)
    
    return {
        "items": tickets,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get support ticket details (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket


@router.patch("/tickets/{ticket_id}/status", response_model=SupportTicketResponse)
async def update_ticket_status(
    ticket_id: UUID,
    request: UpdateTicketStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update support ticket status (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = request.status
    if request.status == "resolved" and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()
    elif request.status != "resolved" and ticket.resolved_at:
        ticket.resolved_at = None
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.patch("/tickets/{ticket_id}/priority", response_model=SupportTicketResponse)
async def update_ticket_priority(
    ticket_id: UUID,
    request: UpdateTicketPriorityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update support ticket priority (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.priority = request.priority
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.get("/tickets/{ticket_id}/comments", response_model=List[TicketCommentResponse])
async def get_ticket_comments(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get ticket comments (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    query = select(TicketComment).where(TicketComment.ticket_id == ticket_id).order_by(TicketComment.created_at)
    results = await db.execute(query)
    comments = results.scalars().all()
    
    return comments


@router.post("/tickets/{ticket_id}/comments", response_model=TicketCommentResponse)
async def create_ticket_comment(
    ticket_id: UUID,
    request: CreateTicketCommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Create a ticket comment (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    comment = TicketComment(
        ticket_id=ticket_id,
        user_id=current_user.id,
        comment=request.comment,
        is_admin=True,
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    return comment


@router.get("/activity", response_model=AdminActivityResponse)
async def get_recent_activity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get recent admin activity (users and support tickets)."""
    items: list[dict] = []

    # Recent users
    users_result = await db.execute(select(User).order_by(User.created_at.desc()).limit(5))
    for user in users_result.scalars().all():
        items.append({
            "id": f"user:{user.id}",
            "type": "user_registered",
            "title": "New user registered",
            "detail": user.email,
            "timestamp": user.created_at,
        })

    # Recent ticket creations
    tickets_result = await db.execute(
        select(SupportTicket, User)
        .join(User, SupportTicket.user_id == User.id)
        .order_by(SupportTicket.created_at.desc())
        .limit(5)
    )
    for ticket, user in tickets_result.all():
        items.append({
            "id": f"ticket_created:{ticket.id}",
            "type": "ticket_created",
            "title": "New support ticket",
            "detail": f"{ticket.title} • {user.email}",
            "timestamp": ticket.created_at,
        })

    # Recent ticket resolutions
    resolved_result = await db.execute(
        select(SupportTicket, User)
        .join(User, SupportTicket.user_id == User.id)
        .where(SupportTicket.resolved_at.is_not(None))
        .order_by(SupportTicket.resolved_at.desc())
        .limit(5)
    )
    for ticket, user in resolved_result.all():
        items.append({
            "id": f"ticket_resolved:{ticket.id}",
            "type": "ticket_resolved",
            "title": "Ticket resolved",
            "detail": f"{ticket.title} • {user.email}",
            "timestamp": ticket.resolved_at,
        })

    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"items": items[:10]}


@router.get("/system", response_model=AdminSystemInfoResponse)
async def get_system_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get basic system info and health."""
    server_time = datetime.utcnow()
    uptime_seconds = int((server_time - APP_START_TIME).total_seconds())

    database_connected = True
    database_latency_ms: float | None = None
    start = perf_counter()
    try:
        await db.execute(select(1))
        database_latency_ms = round((perf_counter() - start) * 1000, 2)
    except Exception:
        database_connected = False

    environment = "Development" if settings.debug else "Production"

    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "environment": environment,
        "server_time": server_time,
        "uptime_seconds": uptime_seconds,
        "database_connected": database_connected,
        "database_latency_ms": database_latency_ms,
    }
from typing import List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    UserListResponse,
    UserResponse,
    UserStatsResponse,
    AdminActivityResponse,
    AdminSystemInfoResponse,
    UpdateUserRoleRequest,
    SupportTicketListResponse,
    SupportTicketResponse,
    UpdateTicketStatusRequest,
    UpdateTicketPriorityRequest,
    CreateTicketCommentRequest,
    TicketCommentResponse,
    MessageResponse,
)
from app.api.routes.auth import get_current_user
from app.core.config import get_settings
from app.db.models import User, SupportTicket, TicketComment
from app.db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated admin user."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access admin panel")
    return current_user


@router.get("/stats", response_model=UserStatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get admin dashboard statistics."""
    # Get user stats
    total_users = await db.scalar(select(func.count(User.id)))
    active_users = await db.scalar(select(func.count(User.id)).where(User.is_active))
    admin_users = await db.scalar(select(func.count(User.id)).where(User.is_admin))
    
    # Get ticket stats
    total_tickets = await db.scalar(select(func.count(SupportTicket.id)))
    open_tickets = await db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status == "open"))
    in_progress_tickets = await db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status == "in_progress"))
    resolved_tickets = await db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status == "resolved"))
    closed_tickets = await db.scalar(select(func.count(SupportTicket.id)).where(SupportTicket.status == "closed"))
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
    }


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List all users (admin only)."""
    query = select(User).offset(skip).limit(limit)
    results = await db.execute(query)
    users = results.scalars().all()
    
    total = await db.scalar(select(func.count(User.id)))
    
    return {
        "items": users,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get user details (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    request: UpdateUserRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update user role (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = request.is_admin
    await db.commit()
    await db.refresh(user)
    
    return user


@router.patch("/users/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: UUID,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update user active status (admin only)."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    
    return user


@router.get("/tickets", response_model=SupportTicketListResponse)
async def list_support_tickets(
    skip: int = 0,
    limit: int = 50,
    status: str | None = None,
    priority: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List all support tickets (admin only)."""
    query = select(SupportTicket)
    
    if status:
        query = query.where(SupportTicket.status == status)
    if priority:
        query = query.where(SupportTicket.priority == priority)
    
    query = query.offset(skip).limit(limit)
    results = await db.execute(query)
    tickets = results.scalars().all()
    
    count_query = select(func.count(SupportTicket.id))
    if status:
        count_query = count_query.where(SupportTicket.status == status)
    if priority:
        count_query = count_query.where(SupportTicket.priority == priority)
    total = await db.scalar(count_query)
    
    return {
        "items": tickets,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get support ticket details (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket


@router.patch("/tickets/{ticket_id}/status", response_model=SupportTicketResponse)
async def update_ticket_status(
    ticket_id: UUID,
    request: UpdateTicketStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update support ticket status (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = request.status
    if request.status == "resolved" and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()
    elif request.status != "resolved" and ticket.resolved_at:
        ticket.resolved_at = None
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.patch("/tickets/{ticket_id}/priority", response_model=SupportTicketResponse)
async def update_ticket_priority(
    ticket_id: UUID,
    request: UpdateTicketPriorityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update support ticket priority (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.priority = request.priority
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.get("/tickets/{ticket_id}/comments", response_model=List[TicketCommentResponse])
async def get_ticket_comments(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get ticket comments (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    query = select(TicketComment).where(TicketComment.ticket_id == ticket_id).order_by(TicketComment.created_at)
    results = await db.execute(query)
    comments = results.scalars().all()
    
    return comments


@router.post("/tickets/{ticket_id}/comments", response_model=TicketCommentResponse)
async def create_ticket_comment(
    ticket_id: UUID,
    request: CreateTicketCommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Create a ticket comment (admin only)."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    comment = TicketComment(
        ticket_id=ticket_id,
        user_id=current_user.id,
        comment=request.comment,
        is_admin=True,
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    return comment
