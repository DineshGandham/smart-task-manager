from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from app.schemas.task import TaskStatus, TaskPriority, TaskCreate, TaskUpdate, TaskOut
from app.services.task_service import TaskService
from app.core.dependencies import get_task_service

router = APIRouter(prefix= "/tasks", tags=["Tasks"])

@router.get("/", response_model=list[TaskOut])
def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    tag: Optional[str] = Query(None),
    service: TaskService = Depends(get_task_service)
):
    return service.get_all(status= status, priority= priority, tag= tag)

@router.post("/",response_model= TaskOut, status_code= status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create(payload)

@router.patch("/{task_id}",response_model= TaskOut)
def update_task(task_id: str, payload: TaskUpdate, service: TaskService = Depends(get_task_service)):
    return service.update(task_id, payload)

@router.delete("/{task_id}",status_code= status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, service: TaskService = Depends(get_task_service)):
    service.delete(task_id) 
