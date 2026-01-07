"""
Authentication routes: signup, login, logout, token refresh.
"""
from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    AuthResponse,
    JiraCredentialsUpdateRequest,
    JiraProjectKeysUpdateRequest,
    JiraUrlUpdateRequest,
    MessageResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserPasswordUpdateRequest,
    UserProfileUpdateRequest,
    UserResponse,
    UserSignupRequest,
)
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_expiration,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.db.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
settings = get_settings()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> UserResponse:
    """
    Dependency to get current authenticated user from JWT token.
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )
    
    # Verify JWT session in database
    is_valid = await UserService.verify_jwt_session(session, user_id, token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked or expired",
        )
    
    # Get user from database
    user = await UserService.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignupRequest,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user account.
    """
    # Check if user already exists
    existing_user = await UserService.get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await UserService.create_user(
        session=session,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store JWT session in database
    token_expiration = get_token_expiration(access_token)
    if not token_expiration:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract token expiration"
        )
    
    await UserService.update_jwt_session(
        session=session,
        user_id=user.id,
        jwt_token=access_token,
        expires_at=token_expiration
    )
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Authenticate user and return JWT tokens.
    """
    # Authenticate user
    user = await UserService.authenticate_user(
        session=session,
        email=credentials.email,
        password=credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store JWT session in database
    token_expiration = get_token_expiration(access_token)
    if not token_expiration:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract token expiration"
        )
    
    await UserService.update_jwt_session(
        session=session,
        user_id=user.id,
        jwt_token=access_token,
        expires_at=token_expiration
    )
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Logout user and invalidate JWT session.
    """
    await UserService.clear_jwt_session(session, current_user.id)
    
    return MessageResponse(message="Successfully logged out")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Refresh access token using refresh token.
    """
    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Get user ID
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )
    
    # Verify user exists and is active
    user = await UserService.get_user_by_id(session, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Generate new tokens
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update JWT session
    token_expiration = get_token_expiration(new_access_token)
    if not token_expiration:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract token expiration"
        )
    
    await UserService.update_jwt_session(
        session=session,
        user_id=user.id,
        jwt_token=new_access_token,
        expires_at=token_expiration
    )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    """
    Get current authenticated user information.
    """
    return current_user


@router.put("/me/profile", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update current user's profile (name, email).
    """
    user = await UserService.update_profile(
        session=session,
        user_id=current_user.id,
        full_name=profile_data.full_name,
        email=profile_data.email
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use by another account"
        )
    
    return UserResponse.model_validate(user)


@router.put("/me/password", response_model=MessageResponse)
async def update_user_password(
    password_data: UserPasswordUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update current user's password.
    """
    # Get full user object to verify current password
    user = await UserService.get_user_by_id(session, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update to new password
    new_hash = hash_password(password_data.new_password)
    updated_user = await UserService.update_password(
        session=session,
        user_id=current_user.id,
        new_password_hash=new_hash
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return MessageResponse(message="Password updated successfully")


@router.put("/me/jira/credentials", response_model=UserResponse)
async def update_jira_credentials(
    jira_data: JiraCredentialsUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update current user's Jira API token.
    Note: In production, encrypt the token before storing.
    """
    user = await UserService.update_jira_credentials(
        session=session,
        user_id=current_user.id,
        jira_api_token=jira_data.jira_api_token  # TODO: Encrypt in production
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/me/jira/url", response_model=UserResponse)
async def update_jira_base_url(
    jira_data: JiraUrlUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update current user's Jira base URL.
    """
    user = await UserService.update_jira_base_url(
        session=session,
        user_id=current_user.id,
        jira_base_url=jira_data.jira_base_url
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.put("/me/jira/projects", response_model=UserResponse)
async def update_jira_projects(
    project_data: JiraProjectKeysUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update current user's Jira project keys (replaces all existing keys).
    """
    user = await UserService.set_jira_project_keys(
        session=session,
        user_id=current_user.id,
        project_keys=project_data.project_keys
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.post("/me/jira/projects/{project_key}", response_model=UserResponse)
async def add_jira_project(
    project_key: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Add a single Jira project key to current user's list.
    """
    user = await UserService.add_jira_project_key(
        session=session,
        user_id=current_user.id,
        project_key=project_key
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.delete("/me/jira/projects/{project_key}", response_model=UserResponse)
async def remove_jira_project(
    project_key: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Remove a single Jira project key from current user's list.
    """
    user = await UserService.remove_jira_project_key(
        session=session,
        user_id=current_user.id,
        project_key=project_key
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)
