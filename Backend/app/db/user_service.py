"""
User database operations and business logic.
"""
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.db.models import User


class UserService:
    """Service for user-related database operations."""
    
    @staticmethod
    async def create_user(
        session: AsyncSession,
        email: str,
        password: str,
        full_name: str
    ) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            session: Database session
            email: User email
            password: Plain text password
            full_name: User's full name
        
        Returns:
            Created user object
        """
        hashed_password = hash_password(password)
        
        user = User(
            email=email,
            password_hash=hashed_password,
            full_name=full_name
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user
    
    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
        """Get user by email address."""
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
        """Get user by ID."""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate_user(
        session: AsyncSession,
        email: str,
        password: str
    ) -> User | None:
        """
        Authenticate user by email and password.
        
        Args:
            session: Database session
            email: User email
            password: Plain text password
        
        Returns:
            User object if authentication successful, None otherwise
        """
        user = await UserService.get_user_by_email(session, email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    async def update_jwt_session(
        session: AsyncSession,
        user_id: UUID,
        jwt_token: str,
        expires_at: datetime
    ) -> User | None:
        """
        Update user's JWT session token.
        
        Args:
            session: Database session
            user_id: User ID
            jwt_token: JWT token string
            expires_at: Token expiration datetime
        
        Returns:
            Updated user object
        """
        user = await UserService.get_user_by_id(session, user_id)
        
        if user:
            user.jwt_session_token = jwt_token
            user.jwt_session_expires_at = expires_at
            user.last_login = datetime.now(timezone.utc)
            
            await session.commit()
            await session.refresh(user)
        
        return user
    
    @staticmethod
    async def clear_jwt_session(session: AsyncSession, user_id: UUID) -> bool:
        """
        Clear user's JWT session (logout).
        
        Args:
            session: Database session
            user_id: User ID
        
        Returns:
            True if successful
        """
        user = await UserService.get_user_by_id(session, user_id)
        
        if user:
            user.jwt_session_token = None
            user.jwt_session_expires_at = None
            
            await session.commit()
            return True
        
        return False
    
    @staticmethod
    async def verify_jwt_session(
        session: AsyncSession,
        user_id: UUID,
        jwt_token: str
    ) -> bool:
        """
        Verify if JWT token matches user's stored session.
        
        Args:
            session: Database session
            user_id: User ID
            jwt_token: JWT token to verify
        
        Returns:
            True if token is valid and matches stored session
        """
        user = await UserService.get_user_by_id(session, user_id)
        
        if not user or not user.is_active:
            return False
        
        if user.jwt_session_token != jwt_token:
            return False
        
        if not user.jwt_session_expires_at:
            return False
        
        if user.jwt_session_expires_at < datetime.now(timezone.utc):
            return False
        
        return True
    
    @staticmethod
    async def add_jira_project_key(
        session: AsyncSession,
        user_id: UUID,
        project_key: str
    ) -> User | None:
        """Add a Jira project key to user's list."""
        user = await UserService.get_user_by_id(session, user_id)
        
        if user:
            if user.jira_project_keys is None:
                user.jira_project_keys = []
            
            if project_key not in user.jira_project_keys:
                user.jira_project_keys = [*user.jira_project_keys, project_key]
                await session.commit()
                await session.refresh(user)
        
        return user
    
    @staticmethod
    async def remove_jira_project_key(
        session: AsyncSession,
        user_id: UUID,
        project_key: str
    ) -> User | None:
        """Remove a Jira project key from user's list."""
        user = await UserService.get_user_by_id(session, user_id)
        
        if user and user.jira_project_keys:
            user.jira_project_keys = [
                key for key in user.jira_project_keys if key != project_key
            ]
            await session.commit()
            await session.refresh(user)
        
        return user
    
    @staticmethod
    async def update_jira_credentials(
        session: AsyncSession,
        user_id: UUID,
        jira_api_token: str
    ) -> User | None:
        """
        Update user's Jira API token (should be encrypted before passing).
        
        Args:
            session: Database session
            user_id: User ID
            jira_api_token: Encrypted Jira API token
        
        Returns:
            Updated user object
        """
        user = await UserService.get_user_by_id(session, user_id)
        
        if user:
            user.jira_api_token = jira_api_token
            await session.commit()
            await session.refresh(user)
        
        return user
