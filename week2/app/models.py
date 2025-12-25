from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NoteBase(BaseModel):
    content: str


class NoteCreate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActionItemBase(BaseModel):
    text: str
    done: bool = False


class ActionItemCreate(ActionItemBase):
    note_id: Optional[int] = None


class ActionItem(ActionItemBase):
    id: int
    note_id: Optional[int]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ActionItemMarkDoneRequest(BaseModel):
    done: bool = True


class ExtractActionItemsRequest(BaseModel):
    text: str
    save_note: bool = False


class ExtractActionItemsResponse(BaseModel):
    note_id: Optional[int]
    items: list[ActionItem]


class NoteListResponse(BaseModel):
    id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True