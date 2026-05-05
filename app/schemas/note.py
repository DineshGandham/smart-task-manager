from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class NoteCreate(BaseModel):
    title: str = Field(..., min_length= 1, max_length= 200)
    content: str = Field(..., min_length= 1, max_length= 100000)
    tags: list[str] = Field(default_factory= list)
    linked_task_id: Optional[str] = None


    @field_validator("title", "content")
    @classmethod
    def not_blank(cls, v: str) -> str :
        if not v.strip():
            raise ValueError("Field cannot be blank.")

        return v.strip()
    
    @field_validator("tags")
    @classmethod
    def tag_lower_case(cls, v: list[str]) -> list[str]:
        return [tag.strip().lower() for tag in v if tag.strip()]


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length= 1, max_length= 200)
    content: Optional[str] = Field(None, min_length= 1, max_length= 100000)
    tags: Optional[list[str]] = None
    linked_task_id: Optional[str] = None


class NoteOut(BaseModel):
    id : str
    title: str
    content: str
    tags: list[str]
    linked_task_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes" : True}