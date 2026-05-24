from app.models.base import Base
from sqlalchemy import String, Text, DateTime, Date, ARRAY, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)

class TaskModel(Base):

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users._id", ondelete= "CASCADE",), nullable= False, index= True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] =  mapped_column(String(20), nullable=False, default="todo")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    due_date: Mapped[str] = mapped_column(Date, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


    def to_dict(self) -> dict:
        return {
            "id" : self.id,
            "user_id" : self.user_id,
            "title" : self.title,
            "description" : self.description,
            "status" : self.status,
            "priority" : self.priority,
            "due_date" : self.due_date,
            "created_at" : self.created_at,
            "updated_at" : self.updated_at
        }