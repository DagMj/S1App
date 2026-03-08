from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GeneratorConfig(Base):
    __tablename__ = 'generator_configs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1000), default='')
    tema: Mapped[str] = mapped_column(String(100), default='')
    part: Mapped[str] = mapped_column(String(10), default='del1', index=True)
    answer_type: Mapped[str] = mapped_column(String(50), default='number')
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
