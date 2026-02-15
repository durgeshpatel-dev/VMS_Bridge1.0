from __future__ import annotations

import datetime as dt
import uuid
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """
    Users table with authentication, JWT session tracking, and Jira configuration.
    Uses PostgreSQL gen_random_uuid() for proper UUID generation.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    # JWT session tracking
    jwt_session_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    jwt_session_expires_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Jira configuration (encrypted before insert)
    jira_api_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    jira_project_keys: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(20)), nullable=True
    )
    # Base URL for user's Jira instance (e.g. https://example.atlassian.net)
    jira_base_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()"), nullable=False
    )
    last_login: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    scans: Mapped[list["Scan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    assets: Mapped[list["Asset"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    vulnerabilities: Mapped[list["Vulnerability"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    jira_tickets: Mapped[list["JiraTicket"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    jobs: Mapped[list["Job"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    support_tickets: Mapped[list["SupportTicket"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class SupportTicket(Base):
    """
    Support tickets table for user complaints and problems.
    """
    __tablename__ = "support_tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
        server_default=text("'open'")
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        server_default=text("'medium'")
    )
    category: Mapped[str] = mapped_column(String(50), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        onupdate=text("NOW()"),
        nullable=False
    )
    resolved_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="support_tickets")
    comments: Mapped[list["TicketComment"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'closed')",
            name="ck_ticket_status"
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'urgent')",
            name="ck_ticket_priority"
        ),
    )


class TicketComment(Base):
    """
    Comments for support tickets.
    """
    __tablename__ = "ticket_comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("support_tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    comment: Mapped[str] = mapped_column(Text, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )

    # Relationships
    ticket: Mapped["SupportTicket"] = relationship("SupportTicket", back_populates="comments")
    user: Mapped["User"] = relationship("User")


class Scan(Base):
    """
    Scans table for tracking uploaded vulnerability scan files.
    Each scan belongs to a user and stores file metadata.
    """
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size_mb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0")
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="uploaded",
        server_default=text("'uploaded'")
    )
    
    uploaded_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )
    processed_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Keep metadata for additional scan information
    scan_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="scans")
    vulnerabilities: Mapped[list["Vulnerability"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["Job"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )


class Asset(Base):
    """
    Assets table for tracking targets like servers, APIs, infrastructure.
    Each asset is unique per user and tracks when it was first and last seen.
    """
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    asset_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        index=True
    )
    
    asset_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    first_seen: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )
    last_seen: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="assets")
    vulnerabilities: Mapped[list["Vulnerability"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("uq_user_asset", "user_id", "asset_identifier", unique=True),
        CheckConstraint(
            "asset_type IN ('server', 'api', 'load_balancer', 'application', 'network_device', 'dependency', 'container', 'code', 'other')",
            name="ck_asset_type"
        ),
    )


class Vulnerability(Base):
    """
    Vulnerabilities table for actual security findings.
    Links to user, scan, and asset with full tracking of severity, status, and lifecycle.
    """
    __tablename__ = "vulnerabilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    plugin_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cve_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation: Mapped[str | None] = mapped_column(Text, nullable=True)

    scanner_severity: Mapped[str | None] = mapped_column(
        String(20), 
        nullable=True,
        index=True
    )
    
    cvss_score: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 1),
        nullable=True
    )
    cvss_vector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    ml_predicted_risk: Mapped[str | None] = mapped_column(String(20), nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str | None] = mapped_column(String(10), nullable=True)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'open'"),
        index=True
    )

    discovered_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )
    last_seen: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )
    closed_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="vulnerabilities")
    scan: Mapped["Scan"] = relationship(back_populates="vulnerabilities")
    asset: Mapped["Asset"] = relationship(back_populates="vulnerabilities")
    jira_ticket: Mapped["JiraTicket | None"] = relationship(
        back_populates="vulnerability", cascade="all, delete-orphan", uselist=False
    )

    __table_args__ = (
        CheckConstraint(
            "scanner_severity IN ('critical', 'high', 'medium', 'low', 'info')",
            name="ck_scanner_severity"
        ),
        CheckConstraint(
            "cvss_score BETWEEN 0.0 AND 10.0",
            name="ck_cvss_score"
        ),
        CheckConstraint(
            "ml_predicted_risk IN ('critical', 'high', 'medium', 'low', 'info')",
            name="ck_ml_predicted_risk"
        ),
        CheckConstraint(
            "risk_score BETWEEN 0 AND 100",
            name="ck_risk_score"
        ),
        CheckConstraint(
            "status IN ('open', 'ignored', 'fixed', 'false_positive')",
            name="ck_status"
        ),
    )


class JiraTicket(Base):
    """
    Jira tickets table for external tracking reference.
    One vulnerability maps to exactly one Jira ticket (enforced by UNIQUE constraint).
    """
    __tablename__ = "jira_tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )
    
    vulnerability_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vulnerabilities.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    jira_ticket_key: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    jira_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    jira_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="jira_tickets")
    vulnerability: Mapped["Vulnerability"] = relationship(back_populates="jira_ticket")


class Job(Base):
    """
    Jobs table for background processing and async visibility.
    Tracks parsing, ML analysis, Jira creation, and report generation tasks.
    """
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False
    )
    
    scan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    job_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'pending'"),
        index=True
    )
    
    progress: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )
    started_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    completed_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    scan: Mapped["Scan"] = relationship(back_populates="jobs")

    __table_args__ = (
        CheckConstraint(
            "job_type IN ('parse_scan', 'ml_analysis', 'jira_creation', 'report_generation')",
            name="ck_job_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled')",
            name="ck_status"
        ),
        CheckConstraint(
            "progress BETWEEN 0 AND 100",
            name="ck_progress"
        ),
    )


