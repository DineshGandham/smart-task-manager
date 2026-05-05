from app.repositories.base import BaseRepository
from typing import Optional
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.core.exceptions import NotFoundError, ValidationError
from datetime import date

class TaskService:
    def __init__(self, repo: BaseRepository):
        self._repo = repo

    def _to_out(self, raw: dict) -> TaskOut:
        return TaskOut(**raw)
    
    def _assert_exists(self, id: str) -> dict:
        task = self._repo.get_by_id(id)
        if not task:
            raise NotFoundError(resource= "Task", resource_id= id)
        return task
    
    def _validate_due_date(self, due_date: Optional[date]):
        if due_date and due_date < date.today():
            raise ValidationError("due_date cannot be in the past")
    
    def get_all(self, status= None, priority= None, tag= None) -> list[TaskOut]:
       tasks = self._repo.get_all()
       if status: tasks= [t for t in tasks if t["status"] == status.value]
       if priority: tasks= [t for t in tasks if t["priority"] == priority.value]
       if tag: tasks= [t for t in tasks if tag.lower() in t.get("tags", [])]
       return [self._to_out(t) for t in tasks]
    
    def get_by_id(self, id:str) -> TaskOut:
        return self._to_out(self._assert_exists(id))
    
    def create(self, payload: TaskCreate) -> TaskOut:
        self._validate_due_date(payload.due_date)
        return self._to_out(self._repo.create(payload.model_dump(mode="json")))
    
    def update(self, id: str, payload: TaskUpdate) -> TaskOut:
        self._assert_exists(id)
        self._validate_due_date(payload.due_date)

        # exclude_unset=True: only fields the caller sent are changed
        changes = payload.model_dump(mode= "json", exclude_unset= True)
        return self._to_out(self._repo.update(id, changes))
    
    def delete(self, id:str):
        self._assert_exists(id)
        self._repo.delete(id)