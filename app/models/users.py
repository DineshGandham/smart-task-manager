from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean 
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

def _now() -> datetime:
    return datetime.now(timezone.utc)

class UserModel(Base):

    __tablename__ = "users"

    _id: Mapped[str] = mapped_column(String, primary_key= True)
    email: Mapped[str] = mapped_column(String(255), nullable= False, unique= True, index= True)
    username: Mapped[str] = mapped_column(String(50), nullable= False, unique= True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active : Mapped[bool] = mapped_column(Boolean, default= True, nullable= False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone= True), default= _now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone= True), default= _now())


    def to_dict(self) -> dict:
        return {
            "id" : self.id,
            "email" : self.email,
            "username":   self.username,
            "is_active":  self.is_active,
            "created_at": self.created_at,
        }