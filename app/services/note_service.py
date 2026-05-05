from typing import Optional
from app.repositories.base import BaseRepository
from app.schemas.note import NoteOut, NoteCreate, NoteUpdate
from app.core.exceptions import NotFoundError

class NoteService:

    def __init__(self,repo : BaseRepository):
        self._repo = repo
    
    def _to_out(self, raw: dict) -> NoteOut:
        return NoteOut(** raw)
    
    def _assert_exists(self, id :str) -> dict:
        note = self._repo.get_by_id(id)
        if not note:
            raise NotFoundError(resource= "Note", resource_id= id)
        return note
    
    def get_all(self, tag= None, linked_task_id= None) -> list[NoteOut]:
        notes = self._repo.get_all()
        if tag: notes = [n for n in notes if tag.lower() in n.get("tag", [])]
        if linked_task_id : notes = [n for n in notes if n.get("linked_task_id") == linked_task_id]
        return [self._to_out(n) for n in notes]
    
    def get_by_id(self, id: str) -> NoteOut:
        return self._to_out(self._assert_exists(id))
    
    def create(self, payload: NoteCreate) -> NoteOut:
        return self._to_out(self._repo.create(payload.model_dump(mode="json")))
    
    def update(self, id: str, payload: NoteUpdate) -> NoteOut:
        self._assert_exists(id)
        changes = payload.model_dump(mode= "json", exclude_unset= True)
        return self._to_out(self._repo.update(id, changes))
    
    def delete(self, id: str):
        self._assert_exists(id)
        self._repo.delete(id)