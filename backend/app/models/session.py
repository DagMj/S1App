from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PracticeSession(Base):
    __tablename__ = 'practice_sessions'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    mode: Mapped[str] = mapped_column(String(30), index=True)
    status: Mapped[str] = mapped_column(String(20), default='active')
    config_json: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SessionItem(Base):
    __tablename__ = 'session_items'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey('practice_sessions.id', ondelete='CASCADE'), index=True)
    problem_id: Mapped[str] = mapped_column(String(36), ForeignKey('problem_instances.id', ondelete='CASCADE'), index=True)
    order_index: Mapped[int] = mapped_column(Integer)
    generator_key: Mapped[str] = mapped_column(String(100), index=True)
    part: Mapped[str] = mapped_column(String(10), index=True)
    max_points: Mapped[float] = mapped_column(Float, default=1.0)
    is_answered: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Submission(Base):
    __tablename__ = 'submissions'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey('practice_sessions.id', ondelete='CASCADE'), index=True)
    session_item_id: Mapped[str] = mapped_column(String(36), ForeignKey('session_items.id', ondelete='CASCADE'), index=True)
    problem_id: Mapped[str] = mapped_column(String(36), ForeignKey('problem_instances.id', ondelete='CASCADE'), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    raw_answer: Mapped[str] = mapped_column(Text)
    normalized_answer: Mapped[str] = mapped_column(Text, default='')
    is_correct: Mapped[bool] = mapped_column(Boolean)
    score: Mapped[float] = mapped_column(Float)
    max_points: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    uncertain: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback: Mapped[str] = mapped_column(Text, default='')
    evaluation_json: Mapped[dict] = mapped_column(JSON, default=dict)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
