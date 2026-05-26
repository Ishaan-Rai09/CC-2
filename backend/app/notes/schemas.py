from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NoteCreate(BaseModel):
    title: str
    subject: str
    description: Optional[str] = None


class NoteOut(BaseModel):
    id: int
    title: str
    subject: str
    description: Optional[str]
    file_key: Optional[str]
    file_url: Optional[str]
    file_name: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None


class NoteListResponse(BaseModel):
    notes: list[NoteOut]
    total: int
