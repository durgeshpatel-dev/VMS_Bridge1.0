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


class UserLoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


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


# Response schemas
class UserResponse(BaseModel):
    """User response data."""
    id: UUID
    email: str
    full_name: str
    is_active: bool
    jira_project_keys: List[str] | None = None
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
