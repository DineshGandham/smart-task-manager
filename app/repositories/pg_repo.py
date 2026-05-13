from typing import Optional
from datetime import datetime, timezone
from app.repositories.base import BaseRepository
from sqlalchemy.orm import Session
from app.models.task import TaskModel
from app.models.note import NoteModel
from app.repositories.base import BaseRepository
from app.utils.id_generator import generate_id

def _now() -> datetime:
    return datetime.now(timezone.utc)

class PgTaskRepository(BaseRepository[dict]):
    
    def __init__(self, db :Session):
        self._db = db
    

    def get_all(self) -> list[dict]:
        rows = self._db.query(TaskModel).order_by(TaskModel.created_at.desc()).all()

        return [r.to_dict() for r in rows]

    def get_by_id(self, id: str) -> Optional[dict]:
        row = self._db.query(TaskModel).filter(TaskModel.id == id).first()
        return row.to_dict() if row else None

    def create(self, data: dict) -> dict:
        now = _now()
        task = TaskModel(id = generate_id(), created_at= now, updated_at= now, **data)
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return task.to_dict()
    
    def update(self, id: str, data: dict) -> dict:
        task = self._db.query(TaskModel).filter(TaskModel.id == id).first()
        if not task: return None
        for k,v in data.items() :
            setattr(task, k ,v)
        task.updated_at = _now()
        self._db.commit()
        self._db.refresh(task)
        return task.to_dict()
    
    def delete(self, id: str) -> bool:
        task = self._db.query(TaskModel).filter(TaskModel.id == id).first()
        if not task: return False
        self._db.delete(task)
        self._db.commit()
        return True
    

class pgNoteRepository(BaseRepository[dict]):

    def __init__(self,db :Session):
        self._db = db
    
    def get_all(self, id: str) -> list[dict]:
        rows = self._db.query(NoteModel).order_by(NoteModel.created_at.desc()).all()

        return [r.to_dict() for r in rows]

    def get_by_id(self, id: str) -> Optional[dict]:
        row = self._db.query(NoteModel).filter(NoteModel.id == id).first()

        return row.to_dict() if row else None
    
    def create(self, data: dict) -> dict:
        now = _now()
        note = NoteModel(id = generate_id(), created_at = now, updated_at = now, **data)

        self._db.add(note)
        self._db.commit()
        self._db.refresh(note)
        return note.to_dict()
    
    def update(self, id :str, data : dict) -> Optional[dict]:

        note = self._db.query(NoteModel).filter(NoteModel.id == id).first()
        if not note: return None
        for k,v in data.items:
            setattr(note, k , v)
        
        note.updated_at = _now()

        self._db.commit()
        self._db.refresh(note)
        return note.to_dict()
    
    def delete(self, id: str) -> bool:
        note = self._db.query(NoteModel).filter(NoteModel.id == id).first()
        if not note: return False
        
        self._db.delete(None)
        self._db.commit()
        return True
