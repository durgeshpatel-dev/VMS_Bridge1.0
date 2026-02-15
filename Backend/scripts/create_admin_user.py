#!/usr/bin/env python3
"""
Admin User Seeding Script
Creates a default admin user for the VMC Bridge application.
"""
import asyncio
import sys
import os
from pathlib import Path

# Set event loop policy for Windows
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import get_db
from app.db.models import User
from app.core.security import hash_password


async def create_admin_user():
    """Create the default admin user."""
    admin_email = "admin@gmail.com"
    admin_password = "admin@vms1"
    admin_name = "System Administrator"

    async for db in get_db():
        try:
            # Check if admin user already exists
            result = await db.execute(select(User).where(User.email == admin_email))
            existing_admin = result.scalar_one_or_none()
            if existing_admin:
                print(f"Admin user with email {admin_email} already exists.")
                return

            # Create admin user
            admin_user = User(
                full_name=admin_name,
                email=admin_email,
                password_hash=hash_password(admin_password),
                is_active=True,
                is_admin=True
            )

            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)

            print("✅ Admin user created successfully!")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print(f"   Name: {admin_name}")

        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            await db.rollback()
        finally:
            await db.close()
        break


if __name__ == "__main__":
    print("🚀 Creating default admin user...")
    asyncio.run(create_admin_user())