from datetime import datetime, date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskCreate(BaseModel):
    title: str = Field(..., min_length= 1, max_length= 200)
    description: Optional[str] = Field(None, max_length= 2000)
    status: TaskStatus = Field(TaskStatus.TODO)
    priority: TaskPriority = Field(TaskPriority.MEDIUM)
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory= list)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v:str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be blank.")
        return v.strip()
    
    @field_validator("tags")
    @classmethod
    def tags_lower_case(cls, v:list[str]) -> list[str] :
        return [tag.strip().lower() for tag in v if tag.strip()]

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None,min_length= 1, max_length= 200)
    description: Optional[str] = Field(None, max_length= 2000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    tags: list[str] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v:str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be blank.")
        return v.strip() if v else v

class TaskOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[date]
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes" : True}