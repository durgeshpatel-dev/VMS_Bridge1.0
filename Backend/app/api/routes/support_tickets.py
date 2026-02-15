"""API routes for support ticket management."""
from typing import List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    CreateSupportTicketRequest,
    SupportTicketResponse,
    SupportTicketListResponse,
    CreateTicketCommentRequest,
    TicketCommentResponse,
    UpdateTicketStatusRequest,
    UpdateTicketPriorityRequest,
    MessageResponse,
)
from app.api.routes.auth import get_current_user
from app.db.models import User, SupportTicket, TicketComment
from app.db.session import get_db

router = APIRouter(prefix="/support-tickets", tags=["support-tickets"])


@router.post("", response_model=SupportTicketResponse)
async def create_support_ticket(
    request: CreateSupportTicketRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new support ticket."""
    ticket = SupportTicket(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        category=request.category,
    )
    
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.get("", response_model=SupportTicketListResponse)
async def list_user_support_tickets(
    skip: int = 0,
    limit: int = 50,
    status: str | None = None,
    priority: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all support tickets for the current user."""
    query = select(SupportTicket).where(SupportTicket.user_id == current_user.id)
    
    if status:
        query = query.where(SupportTicket.status == status)
    if priority:
        query = query.where(SupportTicket.priority == priority)
    
    query = query.offset(skip).limit(limit)
    results = await db.execute(query)
    tickets = results.scalars().all()
    
    count_query = select(func.count(SupportTicket.id)).where(SupportTicket.user_id == current_user.id)
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


@router.get("/{ticket_id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific support ticket."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow access to user's own tickets
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket")
    
    return ticket


@router.patch("/{ticket_id}/status", response_model=SupportTicketResponse)
async def update_ticket_status(
    ticket_id: UUID,
    request: UpdateTicketStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update support ticket status."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow update to user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")
    
    ticket.status = request.status
    if request.status == "resolved" and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()
    elif request.status != "resolved" and ticket.resolved_at:
        ticket.resolved_at = None
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.patch("/{ticket_id}/priority", response_model=SupportTicketResponse)
async def update_ticket_priority(
    ticket_id: UUID,
    request: UpdateTicketPriorityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update support ticket priority."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow update to user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")
    
    ticket.priority = request.priority
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.get("/{ticket_id}/comments", response_model=List[TicketCommentResponse])
async def get_ticket_comments(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ticket comments."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow access to user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket")
    
    query = select(TicketComment).where(TicketComment.ticket_id == ticket_id).order_by(TicketComment.created_at)
    results = await db.execute(query)
    comments = results.scalars().all()
    
    return comments


@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse)
async def create_ticket_comment(
    ticket_id: UUID,
    request: CreateTicketCommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a ticket comment."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow comments on user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to comment on this ticket")
    
    comment = TicketComment(
        ticket_id=ticket_id,
        user_id=current_user.id,
        comment=request.comment,
        is_admin=current_user.is_admin,
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    return comment


@router.delete("/{ticket_id}", response_model=MessageResponse)
async def delete_support_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a support ticket."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow deletion of user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this ticket")
    
    await db.delete(ticket)
    await db.commit()
    
    return {"message": "Ticket deleted successfully"}
from typing import List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    CreateSupportTicketRequest,
    SupportTicketResponse,
    SupportTicketListResponse,
    CreateTicketCommentRequest,
    TicketCommentResponse,
    UpdateTicketStatusRequest,
    UpdateTicketPriorityRequest,
    MessageResponse,
)
from app.api.routes.auth import get_current_user
from app.db.models import User, SupportTicket, TicketComment
from app.db.session import get_db

router = APIRouter(prefix="/support-tickets", tags=["support-tickets"])


@router.post("", response_model=SupportTicketResponse)
async def create_support_ticket(
    request: CreateSupportTicketRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new support ticket."""
    ticket = SupportTicket(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        category=request.category,
    )
    
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.get("", response_model=SupportTicketListResponse)
async def list_user_support_tickets(
    skip: int = 0,
    limit: int = 50,
    status: str | None = None,
    priority: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all support tickets for the current user."""
    query = select(SupportTicket).where(SupportTicket.user_id == current_user.id)
    
    if status:
        query = query.where(SupportTicket.status == status)
    if priority:
        query = query.where(SupportTicket.priority == priority)
    
    query = query.offset(skip).limit(limit)
    results = await db.execute(query)
    tickets = results.scalars().all()
    
    count_query = select(func.count(SupportTicket.id)).where(SupportTicket.user_id == current_user.id)
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


@router.get("/{ticket_id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific support ticket."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow access to user's own tickets
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket")
    
    return ticket


@router.patch("/{ticket_id}/status", response_model=SupportTicketResponse)
async def update_ticket_status(
    ticket_id: UUID,
    request: UpdateTicketStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update support ticket status."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow update to user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")
    
    ticket.status = request.status
    if request.status == "resolved" and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()
    elif request.status != "resolved" and ticket.resolved_at:
        ticket.resolved_at = None
    
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.patch("/{ticket_id}/priority", response_model=SupportTicketResponse)
async def update_ticket_priority(
    ticket_id: UUID,
    request: UpdateTicketPriorityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update support ticket priority."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow update to user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")
    
    ticket.priority = request.priority
    await db.commit()
    await db.refresh(ticket)
    
    return ticket


@router.get("/{ticket_id}/comments", response_model=List[TicketCommentResponse])
async def get_ticket_comments(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ticket comments."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow access to user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this ticket")
    
    query = select(TicketComment).where(TicketComment.ticket_id == ticket_id).order_by(TicketComment.created_at)
    results = await db.execute(query)
    comments = results.scalars().all()
    
    return comments


@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse)
async def create_ticket_comment(
    ticket_id: UUID,
    request: CreateTicketCommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a ticket comment."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow comments on user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to comment on this ticket")
    
    comment = TicketComment(
        ticket_id=ticket_id,
        user_id=current_user.id,
        comment=request.comment,
        is_admin=current_user.is_admin,
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    return comment


@router.delete("/{ticket_id}", response_model=MessageResponse)
async def delete_support_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a support ticket."""
    ticket = await db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Only allow deletion of user's own tickets or admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this ticket")
    
    await db.delete(ticket)
    await db.commit()
    
    return {"message": "Ticket deleted successfully"}

