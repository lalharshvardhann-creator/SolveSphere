from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import UserRegisterRequest


class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserRegisterRequest) -> User:
        """Register a new user after verifying unique email and hashing password."""
        email_normalized = str(user_in.email).strip().lower()
        existing_user = (
            db.query(User)
            .filter(func.lower(User.email) == email_normalized)
            .first()
        )
        if existing_user:
            raise ValueError(f"Email '{user_in.email}' is already registered.")

        password_hash = get_password_hash(user_in.password)

        user = User(
            name=user_in.name.strip(),
            email=email_normalized,
            password_hash=password_hash,
            role=user_in.role,
            phone=user_in.phone.strip() if user_in.phone else None,
            preferred_language=user_in.preferred_language or "en",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Verify user credentials and return the user if valid."""
        email_normalized = str(email).strip().lower()
        user = (
            db.query(User)
            .filter(func.lower(User.email) == email_normalized)
            .first()
        )
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Fetch user by primary key."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Fetch user by email address."""
        email_normalized = str(email).strip().lower()
        return (
            db.query(User)
            .filter(func.lower(User.email) == email_normalized)
            .first()
        )
