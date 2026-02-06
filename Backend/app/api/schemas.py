"""
Pydantic schemas for authentication requests and responses.
"""
from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Request schemas
class UserSignupRequest(BaseModel):
    """User signup request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    recaptcha_token: str


class UserLoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str
    recaptcha_token: str


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class UserProfileUpdateRequest(BaseModel):
    """User profile update request."""
    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None


class UserPasswordUpdateRequest(BaseModel):
    """User password update request."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class JiraCredentialsUpdateRequest(BaseModel):
    """Jira API credentials update request."""
    jira_api_token: str = Field(..., min_length=1)


class JiraProjectKeysUpdateRequest(BaseModel):
    """Jira project keys update request."""
    project_keys: List[str] = Field(..., min_items=1)


class JiraUrlUpdateRequest(BaseModel):
    """Jira base URL update request."""
    jira_base_url: str = Field(..., min_length=5, max_length=512)


# Response schemas
class UserResponse(BaseModel):
    """User response data."""
    id: UUID
    email: str
    full_name: str
    is_active: bool
    jira_project_keys: List[str] | None = None
    jira_base_url: str | None = None
    created_at: datetime
    last_login: datetime | None = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    """Complete authentication response with user and tokens."""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


# Vulnerability schemas
class AssetResponse(BaseModel):
    """Asset response data."""
    id: UUID
    asset_identifier: str
    asset_type: str
    first_seen: datetime
    last_seen: datetime
    
    class Config:
        from_attributes = True


class VulnerabilityResponse(BaseModel):
    """Vulnerability response data."""
    id: UUID
    scan_id: UUID
    asset_id: UUID
    asset: AssetResponse | None = None
    plugin_id: str | None = None
    cve_id: str | None = None
    title: str
    description: str | None = None
    remediation: str | None = None
    scanner_severity: str
    cvss_score: float | None = None
    cvss_vector: str | None = None
    port: int | None = None
    protocol: str | None = None
    status: str
    discovered_at: datetime
    has_ticket: bool = False
    
    class Config:
        from_attributes = True


class VulnerabilityListResponse(BaseModel):
    """Paginated vulnerability list response."""
    items: List[VulnerabilityResponse]
    total: int
    skip: int
    limit: int


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""
    total_vulnerabilities: int
    total_assets: int
    critical: int
    high: int
    medium: int
    low: int
    info: int


# Ticket schemas
class CreateTicketRequest(BaseModel):
    """Create ticket request."""
    vulnerability_ids: List[UUID] | None = None  # None means create for all vulnerabilities
    title: str | None = None
    description: str | None = None
    priority: str = "Medium"  # High, Medium, Low
    issue_type: str = "Bug"


class TicketResponse(BaseModel):
    """Ticket creation response."""
    ticket_id: str
    ticket_url: str
    vulnerability_ids: List[UUID]
    created_at: datetime


class TicketListResponse(BaseModel):
    """Ticket list response."""
    items: List[TicketResponse]
    total: int
