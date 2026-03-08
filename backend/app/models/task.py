from datetime import datetime, timezone
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProblemInstance(Base):
    __tablename__ = 'problem_instances'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    generator_key: Mapped[str] = mapped_column(String(100), index=True)
    part: Mapped[str] = mapped_column(String(10), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    answer_type: Mapped[str] = mapped_column(String(50))
    correct_answer: Mapped[dict] = mapped_column(JSON)
    solution_short: Mapped[str] = mapped_column(Text)
    solution_steps: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    assets: Mapped[list] = mapped_column(JSON, default=list)
    max_points: Mapped[int] = mapped_column(Integer, default=1)
    seed: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session_item_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('session_items.id', ondelete='SET NULL'), nullable=True)
