from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

def _now() -> datetime:
    return datetime.now(timezone.utc)

class NoteModel(Base):
    __tablename__ = "notes"

    id:             Mapped[str]         = mapped_column(String,         primary_key=True)
    title:          Mapped[str]         = mapped_column(String(200),    nullable=False)
    content:        Mapped[str]         = mapped_column(Text,           nullable=False)
    tags:           Mapped[list[str]]  = mapped_column(ARRAY(String), nullable=False, default=list)
    linked_task_id: Mapped[str | None] = mapped_column(String,         nullable=True)
    created_at:     Mapped[datetime]     = mapped_column(DateTime(timezone=True), default=_now)
    updated_at:     Mapped[datetime]     = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "title":          self.title,
            "content":        self.content,
            "tags":           self.tags or [],
            "linked_task_id": self.linked_task_id,
            "created_at":     self.created_at,
            "updated_at":     self.updated_at,
        }