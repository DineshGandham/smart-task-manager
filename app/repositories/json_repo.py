import json, os
from datetime import date, datetime, timezone
from app.repositories.base import BaseRepository
from app.core.exceptions import StorageError
from app.utils.id_generator import generate_id

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class JsonStore:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_files()

    def _ensure_files(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            if not os.path.exists(self.file_path):
                self._write({"tasks": [], "notes": []})
        except (OSError, PermissionError) as e:
            raise StorageError(f"Cannot initialize data store: {e}")
    
    def _read(self) -> dict:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, PermissionError) as e:
            raise StorageError(f"Failed to read data store: {e}")

    def _write(self, data: dict):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except (OSError, PermissionError) as e:
            raise StorageError(f"Failed to write data store: {e}")
    
    def get_collection(self, key: str) -> list[dict]:
        return self._read().get(key, [])
    
    def save_collection(self, key: str, items: list[dict]):
        data = self._read()
        data[key] = items
        self._write(data)
    
class TaskRepository(BaseRepository[dict]):
    COLLECTION = "tasks"

    def __init__(self, file_path: str):
        self._store = JsonStore(file_path)
    
    def get_all(self):
        return self._store.get_collection(self.COLLECTION)
    
    def get_by_id(self, id: str):
        return next((t for t in self.get_all() if t["id"] == id), None)
    
    def create(self, data: dict):
        now = _now_iso()
        task = {"id": generate_id(),"created_at": now, "updated_at": now, **data}
        tasks = self.get_all()
        tasks.append(task)
        self._store.save_collection(self.COLLECTION, tasks)
        return task
    
    def update(self, id: str, data: dict):
        tasks = self.get_all()
        for i,task in enumerate(tasks):
            if task["id"] == id:
                tasks[i] = {**task, **data, "updated_at": _now_iso()}
                self._store.save_collection(self.COLLECTION, tasks)
                return tasks[i]
        return None

    def delete(self, id: str) -> bool:
        tasks = self.get_all()
        filtered = [t for t in tasks if t["id"] !=id]
        if len(filtered) == len(tasks):
            return False
        self._store.save_collection(self.COLLECTION, filtered)
        return True
    
class NoteRepository(BaseRepository[dict]):
    COLLECTION = "notes"

    def __init__(self,file_path: str):
        self._store = JsonStore(file_path)

    def get_all(self):
        return self._store.get_collection(self.COLLECTION)

    def get_by_id(self, id: str):
        return next((n for n in self.get_all() if n["id"] == id), None)

    def create(self, data: dict):
        now = _now_iso()
        note = {"id": generate_id(), "created_at": now, "updated_at": now, **data}
        notes = self.get_all()
        notes.append(note)
        self._store.save_collection(self.COLLECTION, notes)
        return note

    def update(self, id:str, data: dict):
        notes = self.get_all()
        for i, note in enumerate(notes):
            if note["id"] == id:
                notes[i] = {**note, **data, "updated_at": _now_iso()}
                self._store.save_collection(self.COLLECTION, notes)
                return notes[i]
        return None

    def delete(self, id: str):
        notes = self.get_all()
        filtered = [n for n in notes if n["id"] != id]
        if len(filtered) == len(notes): return False
        self._store.save_collection(self.COLLECTION, filtered)
        return True
