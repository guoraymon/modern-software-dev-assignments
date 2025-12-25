from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from .. import db
from ..models import Note, NoteCreate, NoteListResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=Note)
def create_note(request: NoteCreate) -> Note:
    content = request.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    try:
        note_id = db.insert_note(content)
        note = db.get_note(note_id)
        if note is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve created note")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Note(
        id=note.id,
        content=note.content,
        created_at=note.created_at,
    )


@router.get("/{note_id}", response_model=Note)
def get_single_note(note_id: int) -> Note:
    if note_id <= 0:
        raise HTTPException(status_code=400, detail="Note ID must be a positive integer")

    try:
        note = db.get_note(note_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    return Note(
        id=note.id,
        content=note.content,
        created_at=note.created_at,
    )


@router.get("", response_model=List[NoteListResponse])
def list_notes() -> List[NoteListResponse]:
    try:
        rows = db.list_notes()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return [
        NoteListResponse(
            id=row.id,
            content=row.content,
            created_at=row.created_at,
        )
        for row in rows
    ]


