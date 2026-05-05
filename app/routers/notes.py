from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate
from app.core.dependencies import get_note_service
from app.services.note_service import NoteService

router = APIRouter(prefix= "/notes", tags=["notes"])


@router.get("/", response_model= list[NoteOut])
def list_notes(
        tag: Optional[str] = Query(None),
        linked_task_id: Optional[str] = Query(None),
        service: NoteService = Depends(get_note_service)
):
    return service.get_all(tag= tag, linked_task_id= linked_task_id)


@router.post("/",response_model= NoteOut,status_code= status.HTTP_201_CREATED)
def create_notes(payload: NoteCreate, service: NoteService = Depends(get_note_service)):
    return service.create(payload)

@router.patch("/{note_id}", response_model= NoteOut)
def update_notes(note_id:str ,payload: NoteUpdate, service: NoteService = Depends(get_note_service)):
    return service.update(note_id, payload)

@router.delete("/{note_id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, service: NoteService = Depends(get_note_service)):
    return service.delete(note_id)

