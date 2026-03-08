from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import UserCreate


class AuthService:
    def register_user(self, db: Session, payload: UserCreate) -> User:
        existing = db.execute(select(User).where(User.email == payload.email.lower())).scalar_one_or_none()
        if existing:
            raise ValueError('E-post er allerede registrert')

        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=get_password_hash(payload.password),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, email: str, password: str) -> User | None:
        user = db.execute(select(User).where(User.email == email.lower())).scalar_one_or_none()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


auth_service = AuthService()
