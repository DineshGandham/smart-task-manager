from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import Settings, get_settings
from app.repositories.json_repo import TaskRepository, NoteRepository
from app.repositories.pg_repo import PgTaskRepository, pgNoteRepository
from app.services.task_service import TaskService
from app.services.note_service import NoteService
from app.services.mcp_service import MCPService

# Json file is used for storage

# def get_task_repo(settings: Settings = Depends(get_settings)):
#     return TaskRepository(file_path= settings.DATA_FILE_PATH)

# def get_task_service(repo = Depends(get_task_repo)) -> TaskService:
#     return TaskService(repo= repo)

# def get_note_repo(settings: Settings = Depends(get_settings)):
#     return NoteRepository(file_path= settings.DATA_FILE_PATH)

# def get_note_service(repo = Depends(get_note_repo)) -> NoteService:
#     return NoteService(repo=repo)

def get_task_repo(db : Session = Depends(get_db)) -> PgTaskRepository:

    return PgTaskRepository(db = db)

def get_task_service(repo = Depends(get_task_repo)) -> TaskService: 
    return TaskService(repo= repo)

def get_note_repo(db: Session = Depends(get_db)) -> pgNoteRepository:

    return pgNoteRepository(db= db)

def get_note_service(repo = Depends(get_note_repo)) -> NoteService:

    return NoteService(repo= repo) 

def get_mcp_service(
        task_service: TaskService = Depends(get_task_service),
        note_service: NoteService = Depends(get_note_service)
) -> MCPService:
    return MCPService(task_service= task_service, note_service= note_service)