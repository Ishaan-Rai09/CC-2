from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..auth.utils import get_current_user
from ..auth.models import User
from .schemas import NoteOut, NoteListResponse
from . import service

router = APIRouter(prefix="/api/notes", tags=["Notes"])


@router.get("/", response_model=NoteListResponse)
def list_notes(
    search: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notes = service.get_notes(db, current_user.id, search=search, subject=subject)
    return {"notes": notes, "total": len(notes)}


@router.post("/", response_model=NoteOut)
async def create_note(
    title: str = Form(...),
    subject: str = Form(...),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from .schemas import NoteCreate
    data = NoteCreate(title=title, subject=subject, description=description)
    return await service.create_note(db, data, file, current_user.id)


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_stats(db, current_user.id)


@router.get("/{note_id}", response_model=NoteOut)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_note_by_id(db, note_id, current_user.id)


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service.delete_note(db, note_id, current_user.id)
    return {"message": "Note deleted successfully"}


@router.get("/{note_id}/download")
def download_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    url = service.get_download_url(db, note_id, current_user.id)
    return {"download_url": url}
