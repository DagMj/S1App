from datetime import date as dt_date
import uuid

from sqlalchemy import Date, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProgressDaily(Base):
    __tablename__ = 'progress_daily'
    __table_args__ = (
        UniqueConstraint('user_id', 'date', 'generator_key', 'part', name='uq_progress_daily_dim'),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    date: Mapped[dt_date] = mapped_column(Date, index=True)
    generator_key: Mapped[str] = mapped_column(String(100), index=True)
    part: Mapped[str] = mapped_column(String(10), index=True)
    solved_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    score_sum: Mapped[float] = mapped_column(Float, default=0.0)
