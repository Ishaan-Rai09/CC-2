from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from .models import Note
from .schemas import NoteCreate, NoteUpdate
from ..storage.s3 import upload_file_to_s3, delete_file_from_s3, generate_presigned_url
import mimetypes

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".ppt", ".pptx", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def get_file_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"
    mapping = {
        "pdf": "PDF", "docx": "DOCX", "doc": "DOCX",
        "ppt": "PPT", "pptx": "PPT",
        "png": "Image", "jpg": "Image", "jpeg": "Image", "gif": "Image", "webp": "Image",
    }
    return mapping.get(ext, ext.upper())


async def create_note(db: Session, data: NoteCreate, file: UploadFile | None, user_id: int) -> Note:
    file_key = None
    file_url = None
    file_name = None
    file_type = None
    file_size = None

    if file and file.filename:
        import os
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File type '{ext}' not allowed")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")

        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        result = upload_file_to_s3(content, file.filename, content_type, user_id)
        file_key = result["key"]
        file_url = result["url"]
        file_name = file.filename
        file_type = get_file_type(file.filename)
        file_size = len(content)

    note = Note(
        title=data.title,
        subject=data.subject,
        description=data.description,
        file_key=file_key,
        file_url=file_url,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        user_id=user_id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_notes(db: Session, user_id: int, search: str = None, subject: str = None) -> list[Note]:
    query = db.query(Note).filter(Note.user_id == user_id)
    if search:
        query = query.filter(
            Note.title.ilike(f"%{search}%") | Note.subject.ilike(f"%{search}%")
        )
    if subject:
        query = query.filter(Note.subject.ilike(f"%{subject}%"))
    return query.order_by(Note.created_at.desc()).all()


def get_note_by_id(db: Session, note_id: int, user_id: int) -> Note:
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


def delete_note(db: Session, note_id: int, user_id: int) -> bool:
    note = get_note_by_id(db, note_id, user_id)
    if note.file_key:
        delete_file_from_s3(note.file_key)
    db.delete(note)
    db.commit()
    return True


def get_download_url(db: Session, note_id: int, user_id: int) -> str:
    note = get_note_by_id(db, note_id, user_id)
    if not note.file_key:
        raise HTTPException(status_code=404, detail="No file attached to this note")
    return generate_presigned_url(note.file_key, expiry=3600)


def get_stats(db: Session, user_id: int) -> dict:
    total_notes = db.query(Note).filter(Note.user_id == user_id).count()
    subjects = db.query(Note.subject).filter(Note.user_id == user_id).distinct().count()
    recent = (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.created_at.desc())
        .limit(5)
        .all()
    )
    return {"total_notes": total_notes, "subjects_count": subjects, "recent_uploads": recent}
