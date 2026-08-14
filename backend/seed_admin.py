"""CLI seed script to create initial Admin user for DecisionOS."""

import argparse
import sys
from app.core.constants import UserRole
from app.core.logging import logger
from app.core.security import hash_password
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models.user import User


def seed_admin(email: str, password: str, full_name: str) -> None:
    """Creates or updates an initial Admin user."""
    # Ensure tables exist in target database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email.lower().strip()).first()
        if existing_user:
            logger.info(f"User {email} already exists. Updating role to ADMIN...")
            existing_user.role = UserRole.ADMIN
            existing_user.hashed_password = hash_password(password)
            existing_user.is_active = True
            db.commit()
            logger.info(f"Successfully updated {email} to ADMIN.")
        else:
            admin_user = User(
                email=email.lower().strip(),
                full_name=full_name.strip(),
                hashed_password=hash_password(password),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Successfully created ADMIN user: {email}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding admin user: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed DecisionOS Admin User")
    parser.add_argument("--email", default="admin@example.com", help="Admin email address")
    parser.add_argument("--password", default="password123", help="Admin password (min 8 chars)")
    parser.add_argument("--name", default="System Admin", help="Admin full name")

    args = parser.parse_args()
    seed_admin(email=args.email, password=args.password, full_name=args.name)
